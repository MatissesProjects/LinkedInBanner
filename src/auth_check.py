import os
import asyncio
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

async def run():
    li_at = os.getenv("LI_AT_COOKIE")
    if not li_at:
        print("Error: LI_AT_COOKIE not found in .env file.")
        return

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        
        # Add the li_at cookie
        await context.add_cookies([
            {
                "name": "li_at",
                "value": li_at,
                "domain": ".www.linkedin.com",
                "path": "/",
                "httpOnly": True,
                "secure": True,
                "sameSite": "None"
            }
        ])
        
        page = await context.new_page()
        print("Navigating to LinkedIn...")
        await page.goto("https://www.linkedin.com/feed/")
        
        # Wait for a bit to ensure session is recognized
        await page.wait_for_load_state("networkidle")
        
        # Check if we are on the feed or login page
        current_url = page.url
        print(f"Current URL: {current_url}")
        
        if "login" in current_url or "checkpoint" in current_url:
            print("Failed to authenticate. Redirected to login/checkpoint.")
        else:
            print("Successfully authenticated!")
            await page.screenshot(path="debug_login.png")
            print("Screenshot saved as debug_login.png")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
