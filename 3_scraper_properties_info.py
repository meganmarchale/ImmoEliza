import asyncio
from pathlib import Path
from playwright.async_api import async_playwright
import random
import time

INPUT_FILE = "urls.txt"
OUTPUT_FOLDER = Path("html_pages")
OUTPUT_FOLDER.mkdir(exist_ok=True)

async def download_page(playwright, url, index):
    browser = await playwright.chromium.launch(headless=False)
    context = await browser.new_context(user_agent=random_user_agent())
    page = await context.new_page()

    try:
        print(f"🔗 ({index}) Loading: {url}")
        await page.goto(url, timeout=30000)
        await page.wait_for_load_state('networkidle')
        await asyncio.sleep(random.uniform(2.5, 5.0))
        html = await page.content()

        file_name = OUTPUT_FOLDER / f"page_{index}.html"
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"✅ Saved to {file_name.name}")
    except Exception as e:
        print(f"❌ Failed {url}: {e}")
    finally:
        await browser.close()

def random_user_agent():
    ua_list = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/125 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_2_1) AppleWebKit/537.36 Chrome/124 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/123 Safari/537.36",
    ]
    return random.choice(ua_list)

async def main():
    with open(INPUT_FILE, "r") as f:
        urls = [line.strip() for line in f if line.strip()]

    async with async_playwright() as playwright:
        for idx, url in enumerate(urls, 1):
            await download_page(playwright, url, idx)
            time.sleep(random.uniform(1, 3))

if __name__ == "__main__":
    asyncio.run(main())
