import os
import asyncio
from playwright.async_api import async_playwright
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

def log(message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

async def update_banner(image_path):
    li_at = os.getenv("LI_AT_COOKIE")
    if not li_at:
        raise ValueError("LI_AT_COOKIE not found in environment variables.")

    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found at path: {image_path}")

    async with async_playwright() as p:
        log("Initializing Playwright...")
        browser = await p.chromium.launch(headless=True)
        log("Browser launched (Chromium).")
        
        context = await browser.new_context()
        log("Browser context created.")
        
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
        log("Authentication cookie injected.")
        
        page = await context.new_page()
        log("New page opened. Navigating to LinkedIn Profile...")
        
        try:
            await page.goto("https://www.linkedin.com/in/me/", wait_until="domcontentloaded", timeout=60000)
            log("Profile page reached (DOM loaded).")
        except Exception as e:
            log(f"Navigation timed out or failed: {e}")
            raise

        # Robust wait for the profile page to load
        log("Waiting for 'Edit background' trigger to become interactive...")
        await page.wait_for_selector('button[aria-label="Edit background"]', timeout=30000)
        
        # Check for and close any blocking modals/overlays
        log("Checking for blocking modals or overlays...")
        await page.evaluate('''() => {
            const overlays = document.querySelectorAll('.artdeco-modal-overlay, .artdeco-modal');
            overlays.forEach(el => {
                el.remove();
            });
        }''')
        await asyncio.sleep(2)

        log("Clicking 'Edit background' trigger...")
        await page.wait_for_selector('button[aria-label="Edit background"]', state="visible")
        await page.dispatch_event('button[aria-label="Edit background"]', 'click')
        await asyncio.sleep(3)
        
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
                log("Menu items not immediately visible, retrying trigger click...")
                await page.click('button[aria-label="Edit background"]', force=True)
                await asyncio.sleep(3)
                if await page.is_visible(edit_cover_id_selector):
                    await page.click(edit_cover_id_selector)
                else:
                    await page.wait_for_selector(edit_cover_selector, timeout=10000)
                    await page.click(edit_cover_selector)
        except Exception as e:
            log(f"Failed to find or click 'Edit cover image': {e}")
            raise
        
        log("Waiting for file upload input...")
        await page.wait_for_selector('input[type="file"]', timeout=15000, state="attached")
        
        log(f"Uploading image: {image_path}")
        await page.set_input_files('input[type="file"]', image_path)
        
        log("Waiting for 'Apply' button to appear...")
        apply_button_selector = 'button:has-text("Apply")'
        await page.wait_for_selector(apply_button_selector, timeout=15000)
        
        log("Clicking 'Apply' and waiting for processing...")
        await page.click(apply_button_selector)
        
        # Wait for the dialog to disappear or a success message
        log("Finalizing upload (holding 5s for LinkedIn to save)...")
        await asyncio.sleep(5) 
        
        await browser.close()
        log("Banner update process successful.")

if __name__ == "__main__":
    # Test execution
    test_image = "assets/banner.png"
    if not os.path.exists("assets"):
        os.makedirs("assets")
    
    if not os.path.exists(test_image):
        log(f"Please place a valid banner image at {test_image}")
    else:
        asyncio.run(update_banner(test_image))
