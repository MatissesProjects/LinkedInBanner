import os
import random
import asyncio
import time
import re
import subprocess
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from linkedin_bot import update_banner
from discord_alert import send_alert

load_dotenv()

def get_env_int(name, default):
    try:
        return int(os.getenv(name, default))
    except (ValueError, TypeError):
        return default

def update_workflow_cron(next_run_dt):
    workflow_path = ".github/workflows/banner-sync.yml"
    if not os.path.exists(workflow_path):
        print(f"Error: {workflow_path} not found.")
        return False

    # Cron format: minute hour day month day_of_week
    # We use: MM HH DD MM *
    new_cron = next_run_dt.strftime("%M %H %d %m *")
    print(f"Generated new cron: {new_cron}")

    try:
        with open(workflow_path, "r") as f:
            content = f.read()

        # Regex to find the cron line. We look for the schedule section.
        # We'll use a specific comment tag to make it safer if possible, 
        # or just target the schedule cron.
        pattern = r"(cron:\s*['\"]).*?(['\"])"
        new_content = re.sub(pattern, r"\1" + new_cron + r"\2", content)

        with open(workflow_path, "w") as f:
            f.write(new_content)
        
        print(f"Updated {workflow_path} with new cron.")
        return True
    except Exception as e:
        print(f"Failed to update workflow file: {e}")
        return False

def push_changes():
    # Only attempt to push if in a GitHub Actions environment
    if not os.getenv("GITHUB_ACTIONS"):
        print("Not in GitHub Actions environment. Skipping git push.")
        return False

    try:
        # Configure git
        subprocess.run(["git", "config", "user.name", "github-actions[bot]"], check=True)
        subprocess.run(["git", "config", "user.email", "github-actions[bot]@users.noreply.github.com"], check=True)
        
        # Add, commit and push
        subprocess.run(["git", "add", ".github/workflows/banner-sync.yml"], check=True)
        subprocess.run(["git", "commit", "-m", "chore: schedule next banner sync"], check=True)
        subprocess.run(["git", "push"], check=True)
        
        print("Successfully pushed cron update to repository.")
        return True
    except Exception as e:
        print(f"Failed to push changes to git: {e}")
        return False

async def main():
    print("Execution started.")
    
    # Randomized sleep (robotic jitter) before the actual update
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
        # We'll also add a random number of minutes to be less predictable
        random_minutes = random.randint(0, 59)
        
        next_run = datetime.now(timezone.utc) + timedelta(hours=random_hours, minutes=random_minutes)
        print(f"Next run scheduled for: {next_run.isoformat()} (~{random_hours}h {random_minutes}m from now)")
        
        if update_workflow_cron(next_run):
            push_changes()
            
    except Exception as e:
        print(f"Execution failed: {e}")
        send_alert(str(e), "DYNAMIC_CRON")
        exit(1)

if __name__ == "__main__":
    asyncio.run(main())
