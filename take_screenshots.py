import asyncio
import os
from playwright.async_api import async_playwright

async def run():
    out_dir = "/home/Aruuu/int395/screenshots"
    os.makedirs(out_dir, exist_ok=True)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Standard desktop 1080p viewport
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await context.new_page()
        
        print("Navigating to http://127.0.0.1:8000...")
        await page.goto("http://127.0.0.1:8000", wait_until="networkidle")
        await page.wait_for_timeout(1000)
        
        # 1. Main page / Scanner Home
        await page.screenshot(path=f"{out_dir}/01_scanner_home.png", full_page=False)
        print("Saved 01_scanner_home.png")
        
        # 2. Fill inputs using preset or manual text and click Analyze
        await page.click("button[data-preset='conspiracy']")
        await page.wait_for_timeout(800)
        await page.click("#analyze-btn")
        
        # Wait for sliding analysis drawer to open and animate in
        await page.wait_for_selector("#community-vote-bar, #verdict-banner", timeout=10000)
        await page.wait_for_timeout(1500)
        await page.screenshot(path=f"{out_dir}/02_scanner_results.png", full_page=False)
        print("Saved 02_scanner_results.png")
        
        # 3. Scanner Explanation & Token Attribution close up
        # Scroll the analysis panel slightly
        await page.evaluate("""() => {
            const el = document.getElementById('analysis-drawer') || document.querySelector('.analysis-drawer');
            if (el) el.scrollTop = 180;
        }""")
        await page.wait_for_timeout(800)
        await page.screenshot(path=f"{out_dir}/03_scanner_explanation.png", full_page=False)
        print("Saved 03_scanner_explanation.png")
        
        # 4. Red-Teaming Arena (Tab 2)
        await page.click("button[data-tab='redteam-tab']")
        await page.wait_for_timeout(1000)
        await page.screenshot(path=f"{out_dir}/04_redteam_grid.png", full_page=False)
        print("Saved 04_redteam_grid.png")
        
        # 5. Red-Teaming Category Detail
        # Click the first category card
        first_card = page.locator(".category-card").first
        await first_card.click()
        await page.wait_for_timeout(1000)
        await page.screenshot(path=f"{out_dir}/05_redteam_detail.png", full_page=False)
        print("Saved 05_redteam_detail.png")
        
        # 6. Dataset & Transparency Tab (Tab 3)
        await page.click("button[data-tab='stats-tab']")
        await page.wait_for_timeout(1500)
        await page.screenshot(path=f"{out_dir}/06_dataset_transparency.png", full_page=False)
        print("Saved 06_dataset_transparency.png")
        
        # 7. Chrome Extension Tab (Tab 4)
        await page.click("button[data-tab='extension-tab']")
        await page.wait_for_timeout(1000)
        await page.screenshot(path=f"{out_dir}/07_chrome_extension.png", full_page=False)
        print("Saved 07_chrome_extension.png")
        
        # 8. Sidebar Expanded on Hover
        await page.click("button[data-tab='scanner-tab']")
        await page.wait_for_timeout(800)
        sidebar = page.locator("#sidebar")
        await sidebar.hover()
        await page.wait_for_timeout(1000)
        await page.screenshot(path=f"{out_dir}/08_sidebar_expanded.png", full_page=False)
        print("Saved 08_sidebar_expanded.png")
        
        await browser.close()
        print("All screenshots successfully captured!")

if __name__ == "__main__":
    asyncio.run(run())
