# Track 2 Implementation Plan: LinkedIn Bot Development

## Steps

1. **DOM Discovery**
   - Navigate to `https://www.linkedin.com/in/me/`.
   - Use a script or manual inspection (via screenshots if needed) to find:
     - The "Edit profile background" button (pencil icon).
     - The file input element (usually hidden, triggered by the edit button).
     - The "Apply" or "Save" button in the dialog.

2. **Core Logic (linkedin_bot.py)**
   - Initialize browser context with `li_at` cookie.
   - Navigate to profile.
   - Click the edit background button.
   - Set the input file to `assets/banner.png`.
   - Click the "Apply" button.
   - Wait for the success confirmation or for the dialog to close.

3. **Refinement**
   - Add error handling for missing elements.
   - Use smart waits (e.g., `wait_for_selector`).

4. **Testing**
   - Run the script and verify the change on the profile.
