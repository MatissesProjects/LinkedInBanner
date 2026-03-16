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

def log(message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

async def capture_live_banner(li_at):
    log("Refreshing local banner from LinkedIn...")
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1400, 'height': 900})
        await context.add_cookies([{"name": "li_at", "value": li_at, "domain": ".www.linkedin.com", "path": "/"}])
        page = await context.new_page()
        
        # Navigate to profile
        log("Navigating to profile for capture...")
        await page.goto("https://www.linkedin.com/in/me/", wait_until="networkidle", timeout=60000)
        
        banner_container_selector = '.profile-background-image'
        try:
            log("Waiting for banner container...")
            await page.wait_for_selector(banner_container_selector, timeout=15000)
            
            # Ensure assets directory exists
            if not os.path.exists("assets"):
                os.makedirs("assets")
            
            # Attempt a targeted screenshot of the banner area to match dimensions/framing
            banner_element = await page.query_selector(banner_container_selector)
            if banner_element:
                log("Capturing targeted screenshot of banner area...")
                await banner_element.screenshot(path="assets/banner.png")
                log("Live banner area captured to assets/banner.png")
                return True
            else:
                log("Banner container found but element query failed.")
                
        except Exception as e:
            log(f"Capture failed: {e}")
        finally:
            await browser.close()
    return False

def update_workflow_cron(next_run_dt):
    workflow_path = ".github/workflows/banner-sync.yml"
    if not os.path.exists(workflow_path):
        log(f"Error: {workflow_path} not found.")
        return False
    
    new_cron = next_run_dt.strftime("%M %H %d %m *")
    try:
        with open(workflow_path, "r") as f:
            content = f.read()
        pattern = r"(cron:\s*['\"]).*?(['\"])"
        new_content = re.sub(pattern, r"\1" + new_cron + r"\2", content)
        with open(workflow_path, "w") as f:
            f.write(new_content)
        log(f"Updated workflow cron file locally to: {new_cron}")
        return True
    except Exception as e:
        log(f"Cron file update failed: {e}")
        return False

async def main():
    log("Banner Sync Cycle Started (Update -> Sync).")
    li_at = os.getenv("LI_AT_COOKIE")
    
    try:
        image_path = os.path.join("assets", "banner.png")
        
        # 0. Bootstrap: If the file is entirely missing, pull it once
        if not os.path.exists(image_path):
            log("Banner image missing. Bootstrapping from LinkedIn profile...")
            await capture_live_banner(li_at)
        
        # 1. Update LinkedIn
        # We use the local assets/banner.png (which the user may have updated)
        log(f"Uploading banner from: {image_path}")
        await update_banner(image_path)
        
        # 2. Sync: Capture the result back to local filesystem
        # This ensures the repo reflects the actual live state (with LinkedIn's cropping/compression)
        log("Syncing repository with the new live banner...")
        await capture_live_banner(li_at)
        
        # 3. Schedule next run
        random_hours = random.randint(15, 75)
        random_minutes = random.randint(0, 59)
        next_run = datetime.now(timezone.utc) + timedelta(hours=random_hours, minutes=random_minutes)
        update_workflow_cron(next_run)
            
        log("Sync Cycle Complete. Files updated on disk for GitHub Action to push.")
    except Exception as e:
        log(f"Cycle failed: {e}")
        send_alert(str(e), "DYNAMIC_SYNC")
        exit(1)

if __name__ == "__main__":
    asyncio.run(main())
