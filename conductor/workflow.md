# Project Workflow

The project follows a modular scheduling architecture, running daily checks via GitHub Actions.

1. **Daily Check**: GitHub Action cron job triggers.
2. **State Check**: `main.py` reads `EXECUTION_MODE` and relevant interval/probability variables.
3. **Execution Decision**: Based on `FIXED` vs `RANDOM` logic, decide if an update is needed.
4. **Browser Automation**: `linkedin_bot.py` performs the UI steps to update the banner.
5. **State Update**: Upon success, update `LAST_RUN_DATE` via GitHub REST API.
6. **Failure Alert**: On any error, `discord_alert.py` sends a formatted embed to Discord.
