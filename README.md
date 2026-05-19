# LinkedIn Daily Post Automation

Generates a daily LinkedIn post draft using Claude and sends it to a Discord channel
for review. Runs on a free GitHub Actions schedule.

## How it works

1. GitHub Actions runs `generate_post.py` once a day on a cron schedule.
2. The script picks a topic from `topics.md` (skipping ones in `posted.log`).
3. It generates a post using Claude, matching your voice from `voice_examples.md`.
4. It sends the draft to your Discord channel via webhook.
5. You copy the draft, tweak it if needed, and paste to LinkedIn.

## Setup (one-time, ~15 minutes)

### 1. Create Discord webhook
- Make a private Discord server, create a channel like `#daily-drafts`.
- Channel settings → Integrations → Webhooks → New Webhook → Copy URL.

### 2. Get an Anthropic API key
- Sign up at console.anthropic.com.
- Add some credit ($5 lasts a long time).
- Create an API key from the dashboard.

### 3. Create a private GitHub repo
- Push all these files to it.
- Go to repo Settings → Secrets and variables → Actions → New repository secret.
- Add two secrets:
  - `ANTHROPIC_API_KEY` — your Claude API key
  - `DISCORD_WEBHOOK_URL` — your Discord webhook URL

### 4. Personalize
- Replace placeholders in `voice_examples.md` with your own past posts or writing samples.
- Edit `topics.md` to add topics relevant to you. Remove ones that don't fit.

### 5. Test it
- Go to the Actions tab in GitHub.
- Click "Daily LinkedIn Post" workflow → "Run workflow".
- Check Discord — a draft should appear within a minute.

### 6. Adjust the schedule (optional)
- Default cron is `0 3 * * *` which is 8:00 AM Pakistan time (UTC+5).
- Edit `.github/workflows/daily-post.yml` to change the time.
- Use crontab.guru to convert times.

## Tips

- Keep adding topics to `topics.md` whenever you have an idea — even one line is fine.
- Update `voice_examples.md` every couple of weeks with posts that performed well.
- If a draft is bad, just ignore it. There's no cost to skipping a day.

## Cost

- GitHub Actions: free (well within free tier).
- Anthropic API: ~$0.01-0.05 per post depending on model.
- Discord: free.

Total: a few dollars a year.