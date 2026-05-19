"""
Polls a Discord channel for messages reacted with ✅ by the configured user,
then publishes those posts to LinkedIn via Buffer's GraphQL API.

Marks posted messages with a 📤 reaction so they aren't re-posted.
"""

import os
import re
import sys
import requests

# ---- Config from environment variables (set as GitHub Secrets) ----
DISCORD_BOT_TOKEN = os.environ["DISCORD_BOT_TOKEN"]
DISCORD_CHANNEL_ID = os.environ["DISCORD_CHANNEL_ID"]
DISCORD_USER_ID = os.environ["DISCORD_USER_ID"]
BUFFER_API_KEY = os.environ["BUFFER_API_KEY"]
BUFFER_CHANNEL_ID = os.environ["BUFFER_CHANNEL_ID"]

# ---- Constants ----
APPROVE_EMOJI = "✅"
POSTED_EMOJI = "📤"

# LinkedIn limit enforced by Buffer (undocumented but real)
LINKEDIN_CHAR_LIMIT = 1248

DISCORD_API = "https://discord.com/api/v10"
BUFFER_GRAPHQL = "https://api.buffer.com"

DISCORD_HEADERS = {
    "Authorization": f"Bot {DISCORD_BOT_TOKEN}",
    "Content-Type": "application/json",
}

BUFFER_HEADERS = {
    "Authorization": f"Bearer {BUFFER_API_KEY}",
    "Content-Type": "application/json",
}


def fetch_recent_messages(limit: int = 50) -> list[dict]:
    """Fetch the most recent messages from the configured channel."""
    url = f"{DISCORD_API}/channels/{DISCORD_CHANNEL_ID}/messages"
    response = requests.get(url, headers=DISCORD_HEADERS, params={"limit": limit})
    response.raise_for_status()
    return response.json()


def user_reacted(message: dict, emoji: str, user_id: str) -> bool:
    """Check whether a specific user reacted to a message with a given emoji."""
    for reaction in message.get("reactions", []):
        if reaction["emoji"]["name"] != emoji:
            continue
        url = (f"{DISCORD_API}/channels/{DISCORD_CHANNEL_ID}"
               f"/messages/{message['id']}/reactions/{emoji}")
        response = requests.get(url, headers=DISCORD_HEADERS)
        response.raise_for_status()
        users = response.json()
        if any(u["id"] == user_id for u in users):
            return True
    return False


def extract_post_text(message: dict) -> str | None:
    """
    Pull the post text out of a draft message.
    Drafts are wrapped in a triple-backtick code block in send_to_discord().
    """
    content = message.get("content", "")
    match = re.search(r"```\s*(.+?)\s*```", content, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None


def add_reaction(message_id: str, emoji: str) -> None:
    """Add a reaction to a Discord message (URL-encoded emoji)."""
    from urllib.parse import quote
    emoji_encoded = quote(emoji)
    url = (f"{DISCORD_API}/channels/{DISCORD_CHANNEL_ID}"
           f"/messages/{message_id}/reactions/{emoji_encoded}/@me")
    response = requests.put(url, headers=DISCORD_HEADERS)
    response.raise_for_status()


def publish_to_buffer(text: str) -> dict:
    """
    Create a post in Buffer using the GraphQL API and publish it now.

    mode: now      -> publish immediately
    mode: addToQueue -> append to the next queue slot
    """
    if len(text) > LINKEDIN_CHAR_LIMIT:
        raise RuntimeError(
            f"Post is {len(text)} chars; LinkedIn limit via Buffer is "
            f"{LINKEDIN_CHAR_LIMIT}. Trim it and react again."
        )

    mutation = """
    mutation CreatePost($input: CreatePostInput!) {
      createPost(input: $input) {
        ... on PostActionSuccess {
          post { id status }
        }
        ... on MutationError {
          message
        }
      }
    }
    """
    variables = {
        "input": {
            "channelId": BUFFER_CHANNEL_ID,
            "text": text,
            "schedulingType": "automatic",
            "mode": "now",
        }
    }
    response = requests.post(
        BUFFER_GRAPHQL,
        headers=BUFFER_HEADERS,
        json={"query": mutation, "variables": variables},
    )
    response.raise_for_status()
    data = response.json()
    if "errors" in data:
        raise RuntimeError(f"Buffer API error: {data['errors']}")
    result = data["data"]["createPost"]
    if "message" in result:
        raise RuntimeError(f"Buffer rejected post: {result['message']}")
    return result


def main():
    messages = fetch_recent_messages(limit=50)
    print(f"Fetched {len(messages)} recent messages.")

    processed = 0
    for message in messages:
        # Skip messages we've already posted
        if user_reacted(message, POSTED_EMOJI, "@me"):
            continue

        # Only act on messages the user approved
        if not user_reacted(message, APPROVE_EMOJI, DISCORD_USER_ID):
            continue

        post_text = extract_post_text(message)
        if not post_text:
            print(f"Skipping {message['id']}: no post text found.")
            continue

        print(f"Publishing message {message['id']}:")
        print(f"  Preview: {post_text[:80]}...")

        try:
            result = publish_to_buffer(post_text)
            print(f"  Buffer accepted: {result}")
            add_reaction(message["id"], POSTED_EMOJI)
            processed += 1
        except Exception as exc:  # noqa: BLE001
            print(f"  Failed to publish: {exc}", file=sys.stderr)

    print(f"Done. Published {processed} approved post(s).")


if __name__ == "__main__":
    main()