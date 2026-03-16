import os
import asyncio
import random
from playwright.async_api import async_playwright
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

def log(message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

async def human_delay(min_ms=500, max_ms=2000):
    """Small randomized sleep to simulate human reaction time."""
    delay = random.randint(min_ms, max_ms) / 1000.0
    await asyncio.sleep(delay)

async def update_banner(image_path):
    li_at = os.getenv("LI_AT_COOKIE")
    if not li_at:
        raise ValueError("LI_AT_COOKIE not found in environment variables.")

    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found at path: {image_path}")

    # Common Windows Chrome User-Agent
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"

    async with async_playwright() as p:
        log("Initializing Playwright with enhanced Stealth settings...")
        browser = await p.chromium.launch(headless=True)
        
        context = await browser.new_context(
            user_agent=user_agent,
            viewport={'width': 1920, 'height': 1080},
            device_scale_factor=1,
            locale="en-US",
            timezone_id="UTC"
        )
        
        # Comprehensive stealth script
        await context.add_init_script("""
            // Hide automation flags
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            
            // Mock languages and plugins
            Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
            
            // Mock WebGL vendor
            const getParameter = WebGLRenderingContext.prototype.getParameter;
            WebGLRenderingContext.prototype.getParameter = function(parameter) {
                if (parameter === 37445) return 'Intel Inc.';
                if (parameter === 37446) return 'Intel(R) Iris(TM) Graphics 6100';
                return getParameter.apply(this, arguments);
            };

            // Mock Chrome runtime
            window.chrome = { runtime: {} };
        """)
        
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
        log("Stealth context initialized and cookie injected.")
        
        page = await context.new_page()
        
        try:
            log("Navigating to LinkedIn Home (warming up)...")
            await page.goto("https://www.linkedin.com/", wait_until="networkidle", timeout=60000)
            await human_delay(2000, 4000)

            log("Navigating to Profile...")
            await page.goto("https://www.linkedin.com/in/me/", wait_until="networkidle", timeout=90000)
            log(f"Navigation finished. Current URL: {page.url}")
            
            if "login" in page.url or "checkpoint" in page.url or "/in/" not in page.url:
                log(f"WARNING: Authentication failed or redirected: {page.url}")
                await page.screenshot(path="auth_failure.png")
                raise Exception(f"Authentication failed. Please update your LI_AT_COOKIE.")
                
            log("Profile page reached. Simulating human reading...")
            # Scroll down and up to look like a human reading
            await page.mouse.wheel(0, 400)
            await human_delay(1000, 2000)
            await page.mouse.wheel(0, -400)
            await human_delay(1000, 2000)

        except Exception as e:
            log(f"Navigation error: {e}")
            await page.screenshot(path="navigation_error.png")
            raise

        await human_delay(1000, 3000)

        # Robust wait for the profile page to load
        log("Waiting for 'Edit background' trigger...")
        try:
            trigger = page.locator('button[aria-label="Edit background"]')
            await trigger.wait_for(state="visible", timeout=30000)
            
            # Hover before clicking
            await trigger.hover()
            await human_delay(500, 1500)
        except Exception as e:
            log(f"Failed to find 'Edit background' button. Final URL: {page.url}")
            await page.screenshot(path="button_not_found.png")
            raise
        
        # Instead of removing overlays via JS (detectable), we'll try to click naturally
        log("Clicking 'Edit background' trigger...")
        await trigger.click()
        await human_delay(2000, 4000)
        
        log("Searching for 'Edit cover image' menu item...")
        edit_cover_selector = 'text="Edit cover image"'
        
        try:
            # Look for the menu item
            menu_item = page.locator(edit_cover_selector)
            if not await menu_item.is_visible():
                log("Menu not visible, trying trigger click again...")
                await trigger.click()
                await human_delay(1000, 2000)
            
            await menu_item.wait_for(state="visible", timeout=10000)
            await menu_item.hover()
            await human_delay(500, 1000)
            await menu_item.click()
        except Exception as e:
            log(f"Failed to find or click 'Edit cover image': {e}")
            await page.screenshot(path="menu_error.png")
            raise
        
        await human_delay(1000, 2000)
        log("Waiting for file upload input...")
        await page.wait_for_selector('input[type="file"]', timeout=15000, state="attached")
        
        log(f"Uploading image: {image_path}")
        await page.set_input_files('input[type="file"]', image_path)
        await human_delay(2000, 4000)
        
        log("Waiting for 'Apply' button...")
        apply_button_selector = 'button:has-text("Apply")'
        await page.wait_for_selector(apply_button_selector, timeout=15000)
        
        log("Clicking 'Apply'...")
        await page.click(apply_button_selector)
        
        log("Finalizing upload...")
        await asyncio.sleep(8) # Longer wait for save processing
        
        await browser.close()
        log("Banner update successful.")

if __name__ == "__main__":
    test_image = "assets/banner.png"
    if not os.path.exists("assets"): os.makedirs("assets")
    if not os.path.exists(test_image):
        log(f"Please place a valid banner image at {test_image}")
    else:
        asyncio.run(update_banner(test_image))
