# Track 4 Specification: Routing Logic & State Management

## Goals
- Decision-making core that determines if the banner should be updated today.
- Support `FIXED` execution mode (every X days).
- Support `RANDOM` execution mode (based on probability).
- Update the `LAST_RUN_DATE` repository variable on GitHub after successful execution.

## Deliverables
- `src/main.py` as the entry point.
- Integrated GitHub REST API calls for variable updates.
