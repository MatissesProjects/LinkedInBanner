import os
import random
import asyncio
import re
import requests
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from linkedin_bot import update_banner
from discord_alert import send_alert

load_dotenv()

SOURCE_IMAGE_URL = "https://raw.githubusercontent.com/MatissesProjects/GitProgressGraphInfo/main/githeat.png"

def log(message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def download_source_image():
    log(f"Downloading latest source image from: {SOURCE_IMAGE_URL}")
    try:
        if not os.path.exists("assets"):
            os.makedirs("assets")
        
        response = requests.get(SOURCE_IMAGE_URL, timeout=30)
        response.raise_for_status()
        
        with open("assets/banner.png", "wb") as f:
            f.write(response.content)
        
        log("Source image downloaded successfully to assets/banner.png")
        return True
    except Exception as e:
        log(f"Failed to download source image: {e}")
        return False

async def capture_live_banner(li_at):
    log("Refreshing repository with live banner from LinkedIn...")
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1400, 'height': 900})
        await context.add_cookies([{"name": "li_at", "value": li_at, "domain": ".www.linkedin.com", "path": "/"}])
        page = await context.new_page()
        
        log("Navigating to profile for capture...")
        await page.goto("https://www.linkedin.com/in/me/", wait_until="networkidle", timeout=60000)
        
        banner_container_selector = '.profile-background-image'
        try:
            await page.wait_for_selector(banner_container_selector, timeout=15000)
            banner_element = await page.query_selector(banner_container_selector)
            if banner_element:
                log("Capturing live screenshot of the updated banner...")
                await banner_element.screenshot(path="assets/banner.png")
                log("Live banner sync complete.")
                return True
        except Exception as e:
            log(f"Capture failed: {e}")
        finally:
            await browser.close()
    return False

def update_workflow_cron(next_run_dt):
    workflow_path = ".github/workflows/banner-sync.yml"
    if not os.path.exists(workflow_path):
        return False
    # Use format: minute hour day * *
    new_cron = next_run_dt.strftime("%M %H %d * *")
    try:
        with open(workflow_path, "r") as f:
            content = f.read()
        pattern = r"(cron:\s*['\"]).*?(['\"])"
        new_content = re.sub(pattern, r"\1" + new_cron + r"\2", content)
        with open(workflow_path, "w") as f:
            f.write(new_content)
        log(f"Rescheduled next run (Cron: {new_cron})")
        return True
    except Exception as e:
        log(f"Cron update failed: {e}")
        return False

async def main():
    log("Banner Sync Cycle Started (GitHub -> LinkedIn -> Sync).")
    li_at = os.getenv("LI_AT_COOKIE")
    
    try:
        image_path = os.path.join("assets", "banner.png")
        
        # 1. Pull the latest image from the source repository
        download_source_image()
        
        # 2. Update LinkedIn with the new image
        log("Uploading new banner to LinkedIn...")
        await update_banner(image_path)
        
        # 3. Sync: Capture the live result back to the local repository
        # This ensures assets/banner.png in THIS repo matches your live profile
        await capture_live_banner(li_at)
        
        # 4. Schedule next run: +1-3 days from now
        random_days = random.randint(1, 3)
        random_hour = random.randint(0, 23)
        random_minute = random.randint(0, 59)

        # Calculate base date by adding days, then setting randomized hour/minute
        next_run = (datetime.now(timezone.utc) + timedelta(days=random_days)).replace(
            hour=random_hour, minute=random_minute, second=0, microsecond=0
        )

        update_workflow_cron(next_run)

            
        log("Sync Cycle Complete. Changes ready for workflow commit.")
    except Exception as e:
        log(f"Cycle failed: {e}")
        send_alert(str(e), "DYNAMIC_SYNC")
        exit(1)

if __name__ == "__main__":
    asyncio.run(main())
