import os
import random
import asyncio
import time
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import requests
from linkedin_bot import update_banner
from discord_alert import send_alert

load_dotenv()

def get_env_int(name, default):
    try:
        return int(os.getenv(name, default))
    except (ValueError, TypeError):
        return default

def update_github_variable(name, value):
    token = os.getenv("GITHUB_TOKEN")
    repo = os.getenv("GITHUB_REPOSITORY")
    if not token or not repo:
        print("Skipping GitHub variable update: GITHUB_TOKEN or GITHUB_REPOSITORY not set.")
        return False

    url = f"https://api.github.com/repos/{repo}/actions/variables/{name}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    data = {"name": name, "value": str(value)}

    try:
        response = requests.patch(url, headers=headers, json=data)
        response.raise_for_status()
        print(f"Successfully updated GitHub variable {name} to {value}")
        return True
    except Exception as e:
        print(f"Failed to update GitHub variable (ensure Action permissions are set to read/write): {e}")
        return False

def should_run():
    next_run_str = os.getenv("NEXT_RUN_TIME")
    
    # If no next run time is set, we run immediately (and then set it)
    if not next_run_str:
        print("No NEXT_RUN_TIME found. Defaulting to RUN.")
        return True
        
    try:
        next_run = datetime.fromisoformat(next_run_str.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        print(f"Next Run: {next_run.isoformat()} | Now: {now.isoformat()}")
        return now >= next_run
    except Exception as e:
        print(f"Error parsing NEXT_RUN_TIME ({next_run_str}): {e}. Defaulting to RUN.")
        return True

async def main():
    if should_run():
        print("Decision: RUN execution.")
        
        # Randomized sleep (robotic jitter)
        sleep_min = get_env_int("SLEEP_MIN", 0)
        sleep_max = get_env_int("SLEEP_MAX", 300)
        sleep_time = random.randint(sleep_min, sleep_max)
        print(f"Sleeping for {sleep_time} seconds before starting...")
        time.sleep(sleep_time)
        
        try:
            image_path = os.path.join("assets", "banner.png")
            await update_banner(image_path)
            print("Successfully updated banner.")
            
            # Calculate next run: 15 to 75 hours in the future
            random_hours = random.randint(15, 75)
            next_run = datetime.now(timezone.utc) + timedelta(hours=random_hours)
            next_run_str = next_run.isoformat().replace("+00:00", "Z")
            
            print(f"Scheduling next run for ~{random_hours} hours from now: {next_run_str}")
            update_github_variable("NEXT_RUN_TIME", next_run_str)
            
        except Exception as e:
            print(f"Execution failed: {e}")
            send_alert(str(e), "RANDOM_INTERVAL")
            exit(1)
    else:
        print("Decision: SKIP execution (not yet time).")

if __name__ == "__main__":
    asyncio.run(main())
