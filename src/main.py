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
    log("Capturing live banner from LinkedIn to sync repository...")
    async with (await import_playwright()).async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        await context.add_cookies([{"name": "li_at", "value": li_at, "domain": ".www.linkedin.com", "path": "/"}])
        page = await context.new_page()
        await page.goto("https://www.linkedin.com/in/me/", wait_until="domcontentloaded")
        
        banner_selector = '.profile-background-image img'
        try:
            await page.wait_for_selector(banner_selector, timeout=15000)
            banner_img = await page.query_selector(banner_selector)
            img_url = await banner_img.get_attribute('src')
            
            response = requests.get(img_url)
            if response.status_code == 200:
                if not os.path.exists("assets"):
                    os.makedirs("assets")
                with open("assets/banner.png", "wb") as f:
                    f.write(response.content)
                log("Live banner captured and saved to assets/banner.png")
                return True
        except Exception as e:
            log(f"Capture failed: {e}")
            # Fallback: simple screenshot of the area
            try:
                banner_area = await page.query_selector('.profile-background-image')
                if banner_area:
                    if not os.path.exists("assets"):
                        os.makedirs("assets")
                    await banner_area.screenshot(path="assets/banner.png")
                    log("Live banner captured via area-screenshot.")
                    return True
            except:
                pass
        await browser.close()
    return False

async def import_playwright():
    from playwright.async_api import async_playwright
    return type('obj', (object,), {'async_playwright': lambda: async_playwright})

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
    log("Banner Sync & Capture Started (Stateless Workflow Mode).")
    li_at = os.getenv("LI_AT_COOKIE")
    
    try:
        image_path = os.path.join("assets", "banner.png")
        # 1. Update LinkedIn
        await update_banner(image_path)
        
        # 2. Capture the result back to local filesystem
        await capture_live_banner(li_at)
        
        # 3. Calculate and write next schedule to local workflow file
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
