import asyncio
import random
import time
from pathlib import Path
from wakepy import keep
from playwright.async_api import async_playwright

INPUT_FILE = "urls.txt"
OUTPUT_FOLDER = Path("html_pages")
FAILED_FILE = "failed_urls.txt"
OUTPUT_FOLDER.mkdir(exist_ok=True)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/125 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_2_1) AppleWebKit/537.36 Chrome/124 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/123 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0"
]

def get_random_user_agent():
    return random.choice(USER_AGENTS)

async def download_page(playwright, url, index):
    browser = await playwright.chromium.launch(headless=False, slow_mo=30)
    context = await browser.new_context(user_agent=get_random_user_agent())
    page = await context.new_page()

    try:
        print(f"🔗 ({index}) Loading: {url}")
        await page.goto(url, timeout=60000)
        await page.wait_for_load_state('domcontentloaded')
        await asyncio.sleep(random.uniform(3, 5))

        html = await page.content()

        if "captcha-delivery.com" in html or "DataDome" in html:
            print(f"🛑 CAPTCHA detected for {url}. Pause and resolve manually.")
            input("➡️ Passez le CAPTCHA puis appuyez sur Entrée pour continuer...")
            html = await page.content()  # Retry after manual intervention

        file_path = OUTPUT_FOLDER / f"page_{index}.html"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"✅ Saved: {file_path.name}")

    except Exception as e:
        print(f"❌ Error for {url}: {e}")
        with open(FAILED_FILE, "a", encoding="utf-8") as fail_log:
            fail_log.write(f"{url}\n")
    finally:
        await browser.close()

async def main():
    with open(INPUT_FILE, "r") as f:
        urls = [line.strip() for line in f if line.strip()]

    with keep.running():
        async with async_playwright() as playwright:
            for idx, url in enumerate(urls, 1):
                await download_page(playwright, url, idx)
                time.sleep(random.uniform(2, 4))

if __name__ == "__main__":
    asyncio.run(main())
