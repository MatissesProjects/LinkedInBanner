# Project: Dynamic GitHub to LinkedIn Banner Sync

## Objective
Automatically update my personal LinkedIn profile banner using a .png from this repository. The system is highly malleable, supporting multiple scheduling behaviors while maintaining a headless, passwordless setup and alerting via Discord on failure.

## Tech Stack
* Language: Python 3.10+
* Authentication: Passwordless via the LinkedIn `li_at` session cookie.
* Automation: Playwright (for robust headless browser interaction).
* CI/CD: GitHub Actions (Daily Cron trigger).
* State Management: GitHub Repository Variables (`EXECUTION_MODE`, `INTERVAL_DAYS`, `LAST_RUN_DATE`).
* Alerting: Discord Webhook via `requests`.
* Secret Management: GitHub Repository Secrets (`LI_AT_COOKIE`, `DISCORD_WEBHOOK_URL`).

## Repository Structure
Keeping the codebase modular ensures the scraping logic doesn't get tangled with the routing or alerting logic.

    linkedin-banner-sync/
    ├── .github/
    │   └── workflows/
    │       └── banner-sync.yml      # The daily GitHub Action cron job
    ├── src/
    │   ├── main.py                  # Brains: Reads variables, handles routing and sleep logic
    │   ├── linkedin_bot.py          # Muscle: The headless browser (Playwright) to push the image
    │   └── discord_alert.py         # Voice: Constructs and sends the webhook payload
    ├── assets/
    │   └── banner.png               # The actual image file to be uploaded
    ├── requirements.txt             # Dependencies (e.g., requests, playwright)
    ├── plan.md                      # This living document
    └── README.md                    # Setup instructions for grabbing cookies and webhooks

## Execution Architecture: Modular Scheduling Tracks
The workflow runs a daily check-in via GitHub Actions and reads the `EXECUTION_MODE` variable. 

### Track A: "The Clockwork" (Every X Days)
* Variables: `EXECUTION_MODE=FIXED`, `INTERVAL_DAYS=5`, `LAST_RUN_DATE=YYYY-MM-DD`.
* Logic: Calculates the difference between today and `LAST_RUN_DATE`. If the difference is >= `INTERVAL_DAYS`, it triggers a randomized `time.sleep()`, pushes the banner, and updates `LAST_RUN_DATE` via the GitHub REST API. 

### Track B: "The Wildcard" (Pure Randomness)
* Variables: `EXECUTION_MODE=RANDOM`, `PROBABILITY=0.20`.
* Logic: Generates a random float. If <= `PROBABILITY`, it sleeps for a random duration, pushes the banner, and exits. 

## Discord Webhook Payload Definition
If the script catches an exception (e.g., the cookie expires or LinkedIn changes their UI), `discord_alert.py` will format a rich embed and POST it to the Discord Webhook URL. 

We will use environment variables provided by GitHub Actions (like `GITHUB_RUN_ID` and `GITHUB_REPOSITORY`) to generate a direct clickable link to the failed logs.

Expected JSON Payload:

    {
      "content": "<@YOUR_DISCORD_USER_ID> 🚨 LinkedIn Banner Sync Failed!",
      "embeds": [
        {
          "title": "Execution Error Details",
          "description": "The automated banner sync encountered a critical error and exited.",
          "color": 16711680, 
          "fields": [
            {
              "name": "Error Type",
              "value": "`PlaywrightTimeoutError` (or exact Exception name)",
              "inline": true
            },
            {
              "name": "Execution Mode",
              "value": "`FIXED_INTERVAL`",
              "inline": true
            },
            {
              "name": "Action Logs",
              "value": "[Click here to view full GitHub Action logs](https://github.com/USERNAME/REPO/actions/runs/RUN_ID)",
              "inline": false
            }
          ],
          "footer": {
            "text": "Check your li_at cookie in GitHub Secrets or update DOM selectors."
          },
          "timestamp": "2026-03-15T12:00:00.000Z"
        }
      ]
    }

## Implementation Phases

### Phase 1: Environment & Authentication Setup
1. Set up the Python environment, install Playwright (`pip install playwright`, `playwright install`).
2. Extract the `li_at` cookie manually from an active browser session.
3. Write a tiny test script to initialize a headless Chromium browser, inject the `li_at` cookie into the browser context (`context.add_cookies`), and take a screenshot of the LinkedIn homepage to verify successful passwordless login.

### Phase 2: DOM Mapping & Playwright Scripting (linkedin_bot.py)
1. Map out the exact UI steps required on LinkedIn:
   - Navigate to `https://www.linkedin.com/in/me/`.
   - Identify the CSS/XPath selector for the "Edit profile background" pencil icon.
   - Identify the selector for the "Change photo" upload input.
   - Identify the selector for the "Apply/Save" button.
2. Draft the Playwright logic to wait for these elements to load (`page.wait_for_selector()`) to prevent race conditions.
3. Implement the file upload logic (`page.set_input_files()`) using `assets/banner.png`.
4. Run locally and verify the banner updates on the live profile.

### Phase 3: Alerting & Failsafes
1. Generate the Discord Webhook URL.
2. Draft `discord_alert.py` to construct the JSON payload.
3. Wrap the `linkedin_bot.py` execution in a try/except block to catch failures and fire the alert.

### Phase 4: The Routing Logic
1. Draft `main.py` to read environment variables (`EXECUTION_MODE`, etc.).
2. Build the routing statements for FIXED vs RANDOM modes.
3. Integrate the GitHub REST API logic to update `LAST_RUN_DATE` after a successful run.

### Phase 5: GitHub Actions Pipeline
1. Create `.github/workflows/banner-sync.yml`.
2. Map GitHub Secrets and Variables to the Action.
3. Assign read/write Repository Variable permissions to the Action.
