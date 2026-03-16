import os
import requests
import json
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

def send_alert(error_message, execution_mode="UNKNOWN"):
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        print("Error: DISCORD_WEBHOOK_URL not found in environment variables.")
        return

    run_id = os.getenv("GITHUB_RUN_ID", "local-test")
    repo = os.getenv("GITHUB_REPOSITORY", "user/repo")
    log_url = f"https://github.com/{repo}/actions/runs/{run_id}" if run_id != "local-test" else "N/A"

    payload = {
        "content": "🚨 LinkedIn Banner Sync Failed!",
        "embeds": [
            {
                "title": "Execution Error Details",
                "description": "The automated banner sync encountered a critical error and exited.",
                "color": 16711680, # Red
                "fields": [
                    {
                        "name": "Error Message",
                        "value": f"`{error_message}`",
                        "inline": False
                    },
                    {
                        "name": "Execution Mode",
                        "value": f"`{execution_mode}`",
                        "inline": True
                    },
                    {
                        "name": "Action Logs",
                        "value": f"[Click here to view logs]({log_url})" if log_url != "N/A" else "N/A (Local Run)",
                        "inline": False
                    }
                ],
                "footer": {
                    "text": "Check your li_at cookie or update DOM selectors."
                },
                "timestamp": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            }
        ]
    }

    try:
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()
        print("Successfully sent Discord alert.")
    except Exception as e:
        print(f"Failed to send Discord alert: {e}")

if __name__ == "__main__":
    # Test alert
    send_alert("Test error message from local verification script", "FIXED_INTERVAL")
