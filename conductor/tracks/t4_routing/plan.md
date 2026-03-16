# Track 4 Implementation Plan: Routing Logic & State Management

## Steps

1. **Routing Logic (main.py)**
   - Read `EXECUTION_MODE`, `INTERVAL_DAYS`, `PROBABILITY`, `LAST_RUN_DATE` from environment.
   - Implement `should_run_fixed()`: check if `today - last_run >= interval`.
   - Implement `should_run_random()`: check if `random.random() <= probability`.

2. **State Management (GitHub API)**
   - Use `GITHUB_TOKEN` to authenticate.
   - Update `LAST_RUN_DATE` variable via `PATCH /repos/{owner}/{repo}/actions/variables/{name}`.

3. **Execution Wrapper**
   - Wrap the routing and bot call in a try/except block.
   - Fire `discord_alert.send_alert` on failure.
   - Implement random sleep (as per `PLAN.md`) to avoid robotic detection.

4. **Testing**
   - Run `main.py` with various mock environment variables to verify decisions.
