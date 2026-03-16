import os
import random
import asyncio
import time
from datetime import datetime, date
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

def get_env_float(name, default):
    try:
        return float(os.getenv(name, default))
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
        print(f"Failed to update GitHub variable: {e}")
        return False

def should_run():
    mode = os.getenv("EXECUTION_MODE", "FIXED").upper()
    
    if mode == "FIXED":
        last_run_str = os.getenv("LAST_RUN_DATE", "1970-01-01")
        interval = get_env_int("INTERVAL_DAYS", 5)
        
        try:
            last_run = datetime.strptime(last_run_str, "%Y-%m-%d").date()
        except ValueError:
            last_run = date(1970, 1, 1)
            
        days_since = (date.today() - last_run).days
        print(f"Mode: FIXED. Days since last run: {days_since}/{interval}")
        return days_since >= interval
        
    elif mode == "RANDOM":
        probability = get_env_float("PROBABILITY", 0.20)
        roll = random.random()
        print(f"Mode: RANDOM. Rolled {roll:.2f} (Probability: {probability})")
        return roll <= probability
        
    else:
        print(f"Unknown mode: {mode}. Defaulting to run.")
        return True

async def main():
    if should_run():
        print("Decision: RUN execution.")
        
        # Randomized sleep to avoid detection
        sleep_min = get_env_int("SLEEP_MIN", 0)
        sleep_max = get_env_int("SLEEP_MAX", 300)
        sleep_time = random.randint(sleep_min, sleep_max)
        print(f"Sleeping for {sleep_time} seconds before starting...")
        time.sleep(sleep_time)
        
        try:
            image_path = os.path.join("assets", "banner.png")
            await update_banner(image_path)
            
            # Update state
            today_str = date.today().strftime("%Y-%m-%d")
            update_github_variable("LAST_RUN_DATE", today_str)
            
        except Exception as e:
            print(f"Execution failed: {e}")
            send_alert(str(e), os.getenv("EXECUTION_MODE", "UNKNOWN"))
            exit(1)
    else:
        print("Decision: SKIP execution.")

if __name__ == "__main__":
    asyncio.run(main())
