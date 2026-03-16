# Track 5 Implementation Plan: GitHub Actions Integration

## Steps

1. **Workflow Definition**
   - Trigger: `schedule` (daily) and `workflow_dispatch` (manual).
   - Steps:
     - Checkout repository.
     - Set up Python.
     - Install dependencies.
     - Install Playwright browsers.
     - Run `python src/main.py`.

2. **Environment Mapping**
   - Map GitHub Secrets (`LI_AT_COOKIE`, `DISCORD_WEBHOOK_URL`) to environment variables.
   - Map Repository Variables (`EXECUTION_MODE`, `INTERVAL_DAYS`, `PROBABILITY`, `LAST_RUN_DATE`) to environment variables.

3. **Permissions**
   - Ensure the workflow has `contents: read` and `variables: write` (if using a fine-grained token or GITHUB_TOKEN if permissions allow).
   - *Note*: Updating repo variables usually requires a PAT or a specific app token, as the default `GITHUB_TOKEN` might not have `variables: write` permission for the same repo easily.

4. **Testing**
   - Manual trigger of the workflow via GitHub UI.
