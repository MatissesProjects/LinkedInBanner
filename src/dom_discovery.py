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
        print("Navigating to Profile...")
        await page.goto("https://www.linkedin.com/in/me/")
        
        # Wait for a bit to ensure session is recognized
        try:
            await page.wait_for_load_state("networkidle", timeout=15000)
        except:
            print("Network idle timeout, checking page state regardless...")
        
        await asyncio.sleep(5) # Extra buffer
        
        # Capture screenshot for visual inspection
        await page.screenshot(path="profile_debug.png")
        print("Profile screenshot saved as profile_debug.png")
        
        # Look for Edit background button
        edit_bg_button_selector = 'button[aria-label="Edit background"]'
        if await page.is_visible(edit_bg_button_selector):
            print("Clicking Edit background button trigger...")
            await page.click(edit_bg_button_selector)
            await asyncio.sleep(2)
            await page.screenshot(path="dropdown_debug.png")
            print("Dropdown screenshot saved as dropdown_debug.png")
            
            # Find and click the menu item that says "Edit cover image"
            edit_cover_selector = 'text="Edit cover image"'
            if await page.is_visible(edit_cover_selector):
                print("Clicking 'Edit cover image' menu item...")
                await page.click(edit_cover_selector)
                await asyncio.sleep(3)
                await page.screenshot(path="dialog_debug.png")
                print("Dialog screenshot saved as dialog_debug.png")
                
                # Now look for the file input and the apply button in the dialog
                print("\nSearching for file input and Apply button in dialog...")
                file_input = await page.query_selector('input[type="file"]')
                if file_input:
                    print(f"Found File Input: {await file_input.get_attribute('id')}")
                else:
                    print("File input NOT found in dialog.")
                
                # Look for button that says "Apply" or similar
                # Filter buttons in the active modal/dialog
                dialog_buttons = await page.eval_on_selector_all("button", "elements => elements.map(el => ({ ariaLabel: el.ariaLabel, textContent: el.textContent.trim() }))")
                for btn in dialog_buttons:
                    if 'Apply' in btn['textContent'] or 'Save' in btn['textContent']:
                        print(f"Found Dialog Button: {btn['textContent']}")
            else:
                print("'Edit cover image' menu item NOT found.")
        else:
            print("Edit background button NOT found.")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
