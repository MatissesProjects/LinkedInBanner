import os
import asyncio
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

async def update_banner(image_path):
    li_at = os.getenv("LI_AT_COOKIE")
    if not li_at:
        raise ValueError("LI_AT_COOKIE not found in environment variables.")

    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found at path: {image_path}")

    async with async_playwright() as p:
        print("Launching browser...")
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
        print("Navigating to Profile...")
        await page.goto("https://www.linkedin.com/in/me/", wait_until="domcontentloaded")
        
        # Robust wait for the profile page to load
        await page.wait_for_selector('button[aria-label="Edit background"]', timeout=30000)
        
        # Check for and close any blocking modals/overlays
        print("Clearing any blocking overlays...")
        await page.evaluate('''() => {
            const overlays = document.querySelectorAll('.artdeco-modal-overlay, .artdeco-modal');
            overlays.forEach(el => el.remove());
        }''')
        await asyncio.sleep(1)

        print("Clicking 'Edit background' trigger...")
        await page.wait_for_selector('button[aria-label="Edit background"]', state="visible")
        # Try different click methods
        await page.dispatch_event('button[aria-label="Edit background"]', 'click')
        await asyncio.sleep(3)
        await page.screenshot(path="bot_dropdown_debug.png")
        
        print("Waiting for 'Edit cover image' menu item...")
        # Try to find by text directly or by ID if provided
        edit_cover_selector = 'text="Edit cover image"'
        edit_cover_id_selector = '#edit-small'
        
        try:
            # Check for ID first if user suggested it
            if await page.is_visible(edit_cover_id_selector):
                print("Clicking #edit-small...")
                await page.click(edit_cover_id_selector)
            elif await page.is_visible(edit_cover_selector):
                print("Clicking 'Edit cover image' text...")
                await page.click(edit_cover_selector)
            else:
                print("Menu items not visible, trying trigger click again...")
                await page.click('button[aria-label="Edit background"]', force=True)
                await asyncio.sleep(3)
                if await page.is_visible(edit_cover_id_selector):
                    await page.click(edit_cover_id_selector)
                else:
                    await page.wait_for_selector(edit_cover_selector, timeout=10000)
                    await page.click(edit_cover_selector)
        except Exception as e:
            print(f"Failed to find/click 'Edit cover image': {e}")
            # Fallback: log what's visible
            items = await page.eval_on_selector_all(".artdeco-dropdown__content--visible li", "elements => elements.map(el => el.textContent.trim())")
            print(f"Visible menu items: {items}")
            raise
        
        print("Waiting for file input...")
        # The input is hidden, so we wait for it to be attached, not necessarily visible
        await page.wait_for_selector('input[type="file"]', timeout=15000, state="attached")
        
        print(f"Uploading image: {image_path}")
        await page.set_input_files('input[type="file"]', image_path)
        
        print("Waiting for 'Apply' button...")
        apply_button_selector = 'button:has-text("Apply")'
        await page.wait_for_selector(apply_button_selector, timeout=15000)
        
        print("Clicking 'Apply'...")
        await page.click(apply_button_selector)
        
        # Wait for the dialog to disappear or a success message
        print("Finalizing upload...")
        await asyncio.sleep(5) 
        
        await browser.close()
        print("Banner update process completed.")

if __name__ == "__main__":
    # Test execution
    # Ensure assets/banner.png exists or use a placeholder
    test_image = "assets/banner.png"
    if not os.path.exists("assets"):
        os.makedirs("assets")
    
    # Create a placeholder image if it doesn't exist for testing
    if not os.path.exists(test_image):
        print("Creating placeholder image for testing...")
        # Since I can't easily generate a PNG without extra libs, 
        # I'll just warn and exit if the user hasn't provided one.
        print(f"Please place a valid banner image at {test_image}")
    else:
        asyncio.run(update_banner(test_image))
