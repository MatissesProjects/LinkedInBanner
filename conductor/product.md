# Product Definition: Dynamic GitHub to LinkedIn Banner Sync

## Objective
Automatically update my personal LinkedIn profile banner using a `.png` from this repository. The system is highly malleable, supporting multiple scheduling behaviors while maintaining a headless, passwordless setup and alerting via Discord on failure.

## Key Features
- **Passwordless Login**: Uses `li_at` session cookie.
- **Dynamic Scheduling**: Supports fixed intervals or random probability.
- **Robust Alerting**: Discord webhooks for failure notifications with log links.
- **Headless Execution**: Uses Playwright for browser automation.
- **Stateful CI**: GitHub Actions and repository variables for persistence.
