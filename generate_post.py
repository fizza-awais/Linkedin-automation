"""
Daily LinkedIn post generator.

Picks a topic, generates a post in your voice using OpenAI,
strips any markdown formatting (LinkedIn renders only plain text),
and sends the draft to Discord via webhook.
"""

import os
import re
import random
import requests
from datetime import datetime
from openai import OpenAI

# ---- Config from environment variables (set as GitHub Secrets) ----
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
DISCORD_WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]

# ---- Model config ----
# gpt-4o-mini is cheap and works well. Use gpt-4o for higher quality.
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

    return ("FREESTYLE: Pick an interesting technical or career topic from "
            "full-stack, AI/ML, or developer life. Make it feel authentic "
            "and specific.")


def generate_post(topic: str) -> str:
    """Call OpenAI to generate a LinkedIn post in the user's voice."""
    voice_examples = read_file(VOICE_FILE)

    system_prompt = f"""You are writing a LinkedIn post for a software engineer
with full-stack, AI, and ML experience.

VOICE GUIDELINES — match this style closely:
{voice_examples}

FORMATTING RULES (LinkedIn renders ONLY plain text):
- NEVER use markdown. No **bold**, no *italics*, no _underline_, no # headings.
- NEVER use asterisks around words for emphasis.
- NEVER use numbered lists with bold headers like "1. **Topic**:" — write
  flowing paragraphs instead, or use plain lists like "1) Topic — explanation".
- Use real line breaks between paragraphs (blank line between them).
- Use plain ASCII quotes (' and "), not smart quotes.
- No em-dashes (—); use commas, parentheses, or periods.

CONTENT RULES:
- 100-200 words, occasionally longer if the topic warrants it
- 0-3 hashtags max, only if they feel natural; usually skip them
- No emojis unless the voice examples use them
- Sound human, not like a LinkedIn guru
- Avoid clichés: "I'm excited to share", "game-changer", "let's dive in",
  "Here's what I've found:", "thrilled to announce", "in today's fast-paced world"
- Avoid generic engagement-bait CTAs like "What are your thoughts?" or
  "What do you think?". If you must invite discussion, make it specific to
  the actual content, or just end on a strong observation.
- Open with a specific observation or moment, not a general statement
  about the industry
- Write conversationally — like explaining something to a peer over coffee
- It's OK to be opinionated, admit uncertainty, or share what didn't work"""

    user_prompt = (f"Topic for today's post: {topic}\n\n"
                   f"Write the post now. Output ONLY the post text, "
                   f"no preamble or explanation. Remember: no markdown, "
                   f"no asterisks, no bold headers in lists.")

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


def strip_markdown(text: str) -> str:
    """
    Remove markdown formatting that LinkedIn won't render.
    Safety net in case the model slips up despite the prompt rules.
    """
    # Bold: **text** or __text__  -> text
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"__(.+?)__", r"\1", text)

    # Italics: *text* or _text_  -> text
    # (careful not to match inside words like file_name)
    text = re.sub(r"(?<!\w)\*([^*\n]+?)\*(?!\w)", r"\1", text)
    text = re.sub(r"(?<!\w)_([^_\n]+?)_(?!\w)", r"\1", text)

    # Headings: # text  -> text
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)

    # Inline code: `text` -> text
    text = re.sub(r"`([^`]+?)`", r"\1", text)

    # Smart quotes -> straight quotes
    text = text.replace("\u2018", "'").replace("\u2019", "'")
    text = text.replace("\u201c", '"').replace("\u201d", '"')

    # Em-dashes and en-dashes -> regular dash with spaces
    text = text.replace("\u2014", ", ").replace("\u2013", "-")

    # Collapse 3+ consecutive newlines to just 2 (cleaner paragraph breaks)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def send_to_discord(topic: str, post: str) -> None:
    """Send the draft to Discord using the webhook."""
    today = datetime.now().strftime("%A, %B %d")

    header = f"**📝 Draft for {today}**\n*Topic: {topic}*\n\n```\n"
    footer = "\n```\n\n*React with ✅ to publish via Buffer.*"
    content = header + post + footer

    if len(content) > 1900:
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

    raw_post = generate_post(topic)
    post = strip_markdown(raw_post)

    if raw_post != post:
        print("Note: stripped markdown formatting from the draft.")

    print(f"Generated post:\n{post}\n")

    send_to_discord(topic, post)
    log_topic(topic)
    print("Sent to Discord and logged.")


if __name__ == "__main__":
    main()