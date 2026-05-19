"""
Daily LinkedIn post generator.

Picks a topic, generates a post in your voice using OpenAI,
and sends the draft to Discord via webhook.
"""

import os
import random
import requests
from datetime import datetime
from openai import OpenAI

# ---- Config from environment variables (set as GitHub Secrets) ----
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
DISCORD_WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]

# ---- Model config ----
# gpt-4o-mini is cheap and works well for this. Use gpt-4o for higher quality.
MODEL = "gpt-4o-mini"

# ---- File paths ----
VOICE_FILE = "voice_examples.md"
TOPICS_FILE = "topics.md"
POSTED_LOG = "posted.log"


def read_file(path: str) -> str:
    """Read a file, return empty string if it doesn't exist."""
    if not os.path.exists(path):
        return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def pick_topic() -> str:
    """
    Pick an unused topic from topics.md.
    Topics are lines starting with '- '. Skips ones already in posted.log.
    Falls back to a generic prompt if no topics are available.
    """
    topics_raw = read_file(TOPICS_FILE)
    posted = read_file(POSTED_LOG)

    topics = [
        line.strip()[2:].strip()
        for line in topics_raw.splitlines()
        if line.strip().startswith("- ")
    ]

    unused = [t for t in topics if t not in posted]

    if unused:
        return random.choice(unused)

    # Fallback: ask the model to come up with one
    return "FREESTYLE: Pick an interesting technical or career topic from " \
           "full-stack, AI/ML, or developer life. Make it feel authentic and specific."


def generate_post(topic: str) -> str:
    """Call OpenAI to generate a LinkedIn post in the user's voice."""
    voice_examples = read_file(VOICE_FILE)

    system_prompt = f"""You are writing a LinkedIn post for a software engineer
with full-stack, AI, and ML experience.

VOICE GUIDELINES — match this style closely:
{voice_examples}

RULES:
- 100-200 words, occasionally longer if the topic warrants it
- No hashtag spam (0-3 hashtags max, only if natural)
- No emojis unless the voice examples use them
- Sound human, not like a LinkedIn guru
- Avoid clichés like "I'm excited to share" or "game-changer"
- Open with a hook that's a specific observation, not a question
- End with something that invites thought, not a generic CTA
- Use short paragraphs with line breaks between them
- No em-dashes; use commas, parentheses, or periods instead"""

    user_prompt = f"Topic for today's post: {topic}\n\nWrite the post now. " \
                  f"Output ONLY the post text, no preamble or explanation."

    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model=MODEL,
        max_tokens=1024,
        temperature=0.8,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    return response.choices[0].message.content.strip()


def send_to_discord(topic: str, post: str) -> None:
    """Send the draft to Discord using the webhook."""
    today = datetime.now().strftime("%A, %B %d")

    # Discord limits each message to 2000 chars; split if needed.
    header = f"**📝 Draft for {today}**\n*Topic: {topic}*\n\n```\n"
    footer = "\n```\n\n*Copy, tweak if needed, paste to LinkedIn.*"

    content = header + post + footer

    if len(content) > 1900:
        # Send header + post separately, then footer
        requests.post(DISCORD_WEBHOOK_URL, json={
            "content": f"**📝 Draft for {today}**\n*Topic: {topic}*"
        }).raise_for_status()
        requests.post(DISCORD_WEBHOOK_URL, json={
            "content": f"```\n{post[:1900]}\n```"
        }).raise_for_status()
        if len(post) > 1900:
            requests.post(DISCORD_WEBHOOK_URL, json={
                "content": f"```\n{post[1900:]}\n```"
            }).raise_for_status()
    else:
        requests.post(DISCORD_WEBHOOK_URL, json={"content": content}).raise_for_status()


def log_topic(topic: str) -> None:
    """Append the used topic to posted.log so we don't repeat it."""
    with open(POSTED_LOG, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now().isoformat()} | {topic}\n")


def main():
    topic = pick_topic()
    print(f"Topic: {topic}")

    post = generate_post(topic)
    print(f"Generated post:\n{post}\n")

    send_to_discord(topic, post)
    log_topic(topic)
    print("Sent to Discord and logged.")


if __name__ == "__main__":
    main()