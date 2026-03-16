# LinkedIn Banner Sync

Automatically update your LinkedIn profile banner with a randomized window of **15 to 75 hours** using Playwright and GitHub Actions.

## How it Works
This project uses a "Self-Modifying Workflow" strategy:
1. The script runs the banner update.
2. It calculates a random time (15-75 hours in the future).
3. It generates a new Cron schedule and edits `.github/workflows/banner-sync.yml`.
4. It commits and pushes the change back to the repository, scheduling the next run.

## Setup Instructions

### 1. Extract LinkedIn Cookie
- Log in to LinkedIn in your browser.
- Open DevTools (F12) > Application > Cookies > `https://www.linkedin.com`.
- Copy the value of the `li_at` cookie.

### 2. Discord Webhook (Optional)
- Create a Discord Webhook in your server settings to receive failure alerts.

### 3. GitHub Secrets
Go to **Settings > Secrets and variables > Actions > Secrets** and add:
- `LI_AT_COOKIE`: Your `li_at` cookie value.
- `DISCORD_WEBHOOK_URL`: Your Discord Webhook URL.

### 4. CRITICAL: Workflow Permissions
To allow the script to self-schedule, you **must** enable write permissions:
- Go to your repository **Settings > Actions > General**.
- Under **Workflow permissions**, select **"Read and write permissions"**.
- Click **Save**.

## Local Development
```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
python src/main.py
```
Ensure a `.env` file exists with the same keys as the GitHub Secrets.
