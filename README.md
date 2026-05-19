# LinkedIn Daily Post Automation

Generates a daily LinkedIn post draft using OpenAI, sends it to your Discord
channel for review, and publishes approved posts to LinkedIn via Buffer.
Runs entirely on free GitHub Actions — no servers to host or maintain.

## How it works

```
8:00 AM daily
  ↓
GitHub Actions runs generate_post.py
  ↓
Script picks a topic, generates a post with OpenAI, sends to Discord
  ↓
You see the draft in Discord, react with ✅ to approve (or ignore to skip)
  ↓
Every 15 min: GitHub Actions runs publish_approved.py
  ↓
Script checks Discord for ✅ reactions and publishes to Buffer
  ↓
Buffer pushes to LinkedIn, script marks the message with 📤
```

## File overview

| File | Purpose |
|---|---|
| `generate_post.py` | Generates daily draft, sends to Discord |
| `publish_approved.py` | Checks for ✅ reactions, publishes to LinkedIn |
| `.github/workflows/daily-post.yml` | Cron for daily generation (8 AM PKT) |
| `.github/workflows/publish-approved.yml` | Cron for publishing (every 15 min) |
| `voice_examples.md` | Your writing samples for tone matching |
| `topics.md` | Backlog of post topics |
| `posted.log` | Auto-updated history of used topics |
| `requirements.txt` | Python dependencies |

## One-time setup

### 1. Create Discord webhook (for receiving drafts)

- Create a private Discord server, add a channel like `#daily-drafts`.
- Right-click the channel → Edit Channel → Integrations → Webhooks → New Webhook.
- Copy the webhook URL. This is `DISCORD_WEBHOOK_URL`.

### 2. Create a Discord bot (for reading reactions)

- Go to discord.com/developers/applications → New Application → name it.
- **Bot** tab in the left sidebar → Reset Token → copy it. This is `DISCORD_BOT_TOKEN`.
- On the same page, scroll to **Privileged Gateway Intents** and turn on **Message Content Intent**.
- **OAuth2 → URL Generator** → check the `bot` scope.
- In the Bot Permissions section that appears, check: **View Channels**, **Read Message History**, **Add Reactions**.
- Copy the generated URL at the bottom, open it, and add the bot to your server.

### 3. Get Discord IDs

- In Discord: Settings → Advanced → turn on **Developer Mode**.
- Right-click your `#daily-drafts` channel → Copy Channel ID. This is `DISCORD_CHANNEL_ID`.
- Right-click your own name anywhere → Copy User ID. This is `DISCORD_USER_ID`.

### 4. Get an OpenAI API key

- Go to platform.openai.com, sign up, add a small amount of credit ($5 lasts months).
- platform.openai.com/api-keys → Create new secret key. This is `OPENAI_API_KEY`.

### 5. Set up Buffer

- Sign up at buffer.com (free plan).
- Connect your LinkedIn account as a channel in the Buffer dashboard.
- Go to Settings → API → Generate API Key. This is `BUFFER_API_KEY`.
- Get your LinkedIn channel ID by running this in a terminal:

  ```bash
  curl -X POST https://api.buffer.com \
    -H "Authorization: Bearer YOUR_BUFFER_API_KEY" \
    -H "Content-Type: application/json" \
    -d '{"query": "{ account { organizations { channels { id name service } } } }"}'
  ```

  Find your LinkedIn entry in the response and copy its `id`. This is `BUFFER_CHANNEL_ID`.

### 6. Push code to a private GitHub repo

Create a new **private** repo on github.com, then push all files in this folder:

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

### 7. Add GitHub Secrets

In your repo: **Settings → Secrets and variables → Actions → New repository secret**.

Add these seven secrets:

| Secret name | Value |
|---|---|
| `OPENAI_API_KEY` | from step 4 |
| `DISCORD_WEBHOOK_URL` | from step 1 |
| `DISCORD_BOT_TOKEN` | from step 2 |
| `DISCORD_CHANNEL_ID` | from step 3 |
| `DISCORD_USER_ID` | from step 3 |
| `BUFFER_API_KEY` | from step 5 |
| `BUFFER_CHANNEL_ID` | from step 5 |

### 8. Personalize your voice

Edit `voice_examples.md` and paste 3-5 of your actual past LinkedIn posts (or
any writing that sounds like you). This is the single biggest quality lever.

Edit `topics.md` to remove topics that don't fit you and add ones that do.

Commit and push:

```bash
git add voice_examples.md topics.md
git commit -m "Personalize voice and topics"
git push
```

## Testing it end-to-end

1. **Generate a test draft.** Go to the **Actions** tab in your repo → **Daily LinkedIn Post** → **Run workflow** → green button. Wait 30-60 seconds. A draft should appear in your Discord channel.

2. **Approve it.** React to the draft message with ✅.

3. **Trigger the publisher manually** (don't wait 15 min for the first test). Actions tab → **Publish Approved Posts** → **Run workflow**. Wait 30-60 seconds.

4. **Verify.** Within a minute you should see:
   - 📤 reaction appear on the Discord message
   - The post appear on your LinkedIn feed (or in Buffer's "sent" tab)

If something fails, the Actions tab shows red X marks with logs. Click into the failed run to see the error.

## Daily routine after setup

You don't have to do anything. The schedule runs automatically. Your only job is:

- Open Discord whenever you want
- See drafts that have piled up
- React ✅ on the ones you like
- Ignore or skip the rest

Posts you approve go live within 15 minutes via Buffer.

## Customization tips

**Change the posting time.** Edit the cron in `.github/workflows/daily-post.yml`. Default is `0 3 * * *` (8 AM Pakistan time = 3 AM UTC). Use crontab.guru to convert.

**Get faster posting.** Change the cron in `publish-approved.yml` from `*/15 * * * *` to `*/5 * * * *` for 5-minute polling.

**Better quality drafts.** In `generate_post.py`, change `MODEL = "gpt-4o-mini"` to `MODEL = "gpt-4o"`. Costs a few cents per post instead of a fraction of a cent.

**More topics.** Add to `topics.md` whenever inspiration hits. Even one line is fine.

**Refresh voice samples.** Every few weeks, update `voice_examples.md` with your best-performing recent posts so the AI keeps tracking your evolving style.

## Cost

- GitHub Actions: free (well within the 2000 min/month free tier).
- OpenAI: ~$0.0001-0.05 per post depending on model.
- Discord: free.
- Buffer: free plan (3 channels, 10 scheduled per channel).

Total: a few dollars a year at most.

## Troubleshooting

**"KeyError: SOME_SECRET"** in workflow logs
The secret name doesn't match exactly. Check spelling and case-sensitivity in repo Settings → Secrets.

**OpenAI 401 error**
API key is wrong, or your account has no credit. Check platform.openai.com/usage.

**Buffer "Please use api.buffer.com" error**
The endpoint in `publish_approved.py` should be `https://api.buffer.com` (no path, no trailing slash). If you migrated from an older version of this code, update the `BUFFER_GRAPHQL` constant.

**Buffer rejects post: too long**
LinkedIn posts via Buffer are capped at 1,248 characters. The script catches this and tells you. Edit the draft in Discord, or just trim your prompt rules in `generate_post.py` to enforce shorter posts.

**Bot doesn't react with 📤 even though ✅ was added**
Check the `publish-approved.yml` run logs. Common causes: bot lacks **Read Message History** permission (re-invite with correct scopes), or **Message Content Intent** isn't enabled on the Discord Developer Portal (Bot tab → Privileged Gateway Intents).

**Discord 403 errors**
The bot isn't in your server, or it's missing channel permissions. Re-add it via the OAuth2 URL with `bot` scope and the three permissions listed above.

**Draft never appears in Discord**
Check the `daily-post.yml` run logs. If it succeeded but Discord is empty, the webhook URL is wrong or revoked. Regenerate the webhook in Discord and update the secret.

**The same topic was used twice**
The script logs used topics to `posted.log` and commits it back. If commits aren't working, check the workflow has `permissions: contents: write`.

## Upgrading later

If you outgrow this setup, natural next steps are:

- **Real-time approvals** — replace the polling workflow with an always-on Discord bot on Railway or Fly.io's free tier.
- **More approval emojis** — add 🔄 to regenerate, ❌ to skip permanently.
- **Smart topic sourcing** — feed your GitHub commits, starred repos, or saved articles into the prompt instead of static topics.
- **Engagement loop** — pull Buffer's analytics (when they expose it) to weight which topics performed well.
- **Direct LinkedIn API** — once you've proven the workflow, apply for LinkedIn's `w_member_social` scope to skip Buffer entirely.

For now though, this setup is intentionally simple. Use it for a few weeks before adding complexity.