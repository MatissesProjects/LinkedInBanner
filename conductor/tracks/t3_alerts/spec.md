# Track 3 Specification: Alerting & Failsafes

## Goals
- Provide immediate notification on script failure.
- Include rich details in the alert (error type, log links, execution mode).
- Ensure the alerting logic is reusable across different failure points.

## Deliverables
- `src/discord_alert.py` with the `send_alert` function.
- Verified test notification in a Discord channel.
