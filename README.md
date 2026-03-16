# LinkedIn Banner Sync

Automatically update your LinkedIn profile banner with a randomized or fixed-interval schedule using Playwright and GitHub Actions.

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

### 4. GitHub Variables
Go to **Settings > Secrets and variables > Actions > Variables** and add:
- `EXECUTION_MODE`: `FIXED` or `RANDOM`.
- `INTERVAL_DAYS`: Number of days between updates (e.g., `5`).
- `PROBABILITY`: Chance of update each day (e.g., `0.20`).
- `LAST_RUN_DATE`: Initial value (e.g., `1970-01-01`). Since the script no longer updates this automatically, you may need to update it manually in GitHub Settings if using `FIXED` mode to skip days.

## Local Development
```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
python src/main.py
```
Ensure a `.env` file exists with the same keys as the GitHub Secrets.
