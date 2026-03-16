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
        log("Initializing Playwright with Stealth settings...")
        browser = await p.chromium.launch(headless=True)
        
        context = await browser.new_context(
            user_agent=user_agent,
            viewport={'width': 1920, 'height': 1080},
            device_scale_factor=1,
            locale="en-US",
            timezone_id="UTC"
        )
        
        # Hide automation flags
        await context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
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
            log("Navigating to LinkedIn Profile...")
            # Use a longer timeout and wait for network idle to be more 'user-like'
            await page.goto("https://www.linkedin.com/in/me/", wait_until="networkidle", timeout=90000)
            log(f"Navigation finished. Current URL: {page.url}")
            
            if "login" in page.url or page.url == "https://www.linkedin.com/":
                log("WARNING: Redirected to login page or home page. Cookie rejected or challenge triggered.")
                await page.screenshot(path="auth_failure.png")
                raise Exception("Authentication failed (redirected to home/login).")
                
            log("Profile page reached.")
        except Exception as e:
            log(f"Navigation error: {e}")
            await page.screenshot(path="navigation_error.png")
            raise

        await human_delay(1000, 3000)

        # Robust wait for the profile page to load
        log("Waiting for 'Edit background' trigger...")
        try:
            await page.wait_for_selector('button[aria-label="Edit background"]', timeout=30000)
        except Exception as e:
            log(f"Failed to find 'Edit background' button. Final URL: {page.url}")
            await page.screenshot(path="button_not_found.png")
            raise
        
        # Check for and close any blocking modals/overlays
        log("Clearing any blocking overlays...")
        await page.evaluate('''() => {
            const overlays = document.querySelectorAll('.artdeco-modal-overlay, .artdeco-modal');
            overlays.forEach(el => el.remove());
        }''')
        await human_delay()

        log("Clicking 'Edit background' trigger...")
        await page.click('button[aria-label="Edit background"]', force=True)
        await human_delay(2000, 4000)
        
        log("Searching for 'Edit cover image' menu item...")
        edit_cover_selector = 'text="Edit cover image"'
        edit_cover_id_selector = '#edit-small'
        
        try:
            if await page.is_visible(edit_cover_id_selector):
                log("Clicking #edit-small (ID match)...")
                await page.click(edit_cover_id_selector)
            elif await page.is_visible(edit_cover_selector):
                log("Clicking 'Edit cover image' (Text match)...")
                await page.click(edit_cover_selector)
            else:
                log("Menu not visible, retrying trigger click...")
                await page.click('button[aria-label="Edit background"]', force=True)
                await human_delay(2000, 3000)
                await page.wait_for_selector(edit_cover_selector, timeout=10000)
                await page.click(edit_cover_selector)
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
