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
        
        print("Clicking 'Edit background' trigger...")
        await page.click('button[aria-label="Edit background"]')
        
        print("Waiting for 'Edit cover image' menu item...")
        await page.wait_for_selector('text="Edit cover image"', timeout=10000)
        await page.click('text="Edit cover image"')
        
        print("Waiting for file input...")
        await page.wait_for_selector('input[type="file"]', timeout=10000)
        
        print(f"Uploading image: {image_path}")
        await page.set_input_files('input[type="file"]', image_path)
        
        print("Waiting for 'Apply' button...")
        apply_button_selector = 'button:has-text("Apply")'
        await page.wait_for_selector(apply_button_selector, timeout=10000)
        
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
