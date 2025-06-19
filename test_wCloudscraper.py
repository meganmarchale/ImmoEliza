import csv
import os
import random
import time
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from wakepy import keep
from fake_useragent import UserAgent
from wakepy import keep

# ----------- CONFIG ----------- #
HEADERS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.96 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.5672.126 Safari/537.36",
]

OUTPUT_FILE = "immoweb_data.csv"
INPUT_FILE = "urls.txt"  # one URL per line
FIELDS = [
    "url", "title", "price", "property_type", "subtype", "postal_code", "bedrooms", "surface",
    "condition", "kitchen", "terrace", "terrace_surface", "land_surface", "agency_name"
]

"""XPATHS = {
    "price": ('//*[@id="classified-header"]/div/div/div[1]/div/div[1]/p/span[1]', int),
    "bedrooms": ('//*[@id="accordion_5f72cb3c-c9e4-4ee4-9cf7-aaa91f0ea62e"]/table/tbody/tr[6]/td', int),
    "surface": ('//*[@id="accordion_5f72cb3c-c9e4-4ee4-9cf7-aaa91f0ea62e"]/table/tbody/tr[1]/t', int),
    "condition": ('#accordion_c9fcfeed-9870-4eb1-99c7-5bfd4310e821 > table > tbody > tr:nth-child(2) > td', str),
    "kitchen": ('//*[@id="accordion_5f72cb3c-c9e4-4ee4-9cf7-aaa91f0ea62e"]/table/tbody/tr[5]/td', str),
    "land_surface": ('//*[@id="accordion_5ecd00b8-479b-443c-ae9e-f5ac53e1d01c"]/table/tbody/tr[1]/td', int),
    "postal_code" : ('//*[@id="classified-header"]/div/div/div[1]/div/div[2]/div[1]/div/button/span[1]', str),
    "agency_name" : ('//*[@id="classified-header"]/div/div/div[1]/div/div[3]/a', str)
}"""


    SELECTOR = {
        "price": ("#classified-header > div > div > div.grid__item.desktop--9 > div > div.classified__header-primary-info > p > span:nth-child(1)"),
        "bedrooms": ("#accordion_5f72cb3c-c9e4-4ee4-9cf7-aaa91f0ea62e > table > tbody > tr:nth-child(6) > td")

    }

def get_random_user_agent():
    return random.choice(HEADERS)

def extract_element(driver, selector, cast=str):
    try:
        el = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
        )
        text = el.text.strip().replace("\u202f", "")
        return cast(text) if text else ""
    except:
        return ""

async def download_page(playwright, url, index):
    browser = await playwright.chromium.launch(headless=False, slow_mo=30)
    context = await browser.new_context(user_agent=get_random_user_agent())
    page = await context.new_page()

    try:
        print(f"({index}) Loading: {url}")
        await page.goto(url, timeout=60000)
        await page.wait_for_load_state('domcontentloaded')
        await asyncio.sleep(random.uniform(3, 5))

        html = await page.content()

        if "captcha-delivery.com" in html or "DataDome" in html:
            print(f"CAPTCHA detected for {url}. Pause and resolve manually.")
            input("Passez le CAPTCHA puis appuyez sur Entrée pour continuer...")
            html = await page.content()  # Retry after manual intervention

        file_path = OUTPUT_FOLDER / f"page_{index}.html"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"Saved: {file_path.name}")

    except Exception as e:
        print(f"Error for {url}: {e}")
        with open(FAILED_FILE, "a", encoding="utf-8") as fail_log:
            fail_log.write(f"{url}\n")
    finally:
        await browser.close()

def already_scraped(url):
    if not Path(OUTPUT_FILE).exists():
        return False
    with open(OUTPUT_FILE, newline='') as f:
        return url in f.read()


def scrape_url(driver, url):
    print(f"Scraping: {url}")
    driver.get(url)
    time.sleep(2)
    
    data = {"url": url}
    data["title"] = driver.title.strip()
    for key, (selector, cast) in SELECTOR.items():
        data[key] = extract_element(driver, selector, cast)


    data["terrace"] = "Yes" if data.get("terrace_surface") else ""
    data["property_type"] = "house" if "/houses/" in url else ""
    data["subtype"] = "new_project"
    data["postal_code"] = url.split("/")[7] if len(url.split("/")) > 7 else ""
    data["agency_name"] = "" 

    return data

# ----------- DRIVER INIT ----------- #
def init_driver():
    chrome_options = Options()
    chrome_options.add_argument(f"--user-agent={get_random_user_agent()}")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--window-size=1920,1080")
    return webdriver.Chrome(options=chrome_options)

# ----------- MAIN LOOP ----------- #
def main():
    with keep.running():
        with open(INPUT_FILE) as f:
            urls = [line.strip() for line in f if line.strip()]

        driver = init_driver()

        with open(OUTPUT_FILE, mode="a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS)
            if os.stat(OUTPUT_FILE).st_size == 0:
                writer.writeheader()

            for i, url in enumerate(urls):
                if already_scraped(url):
                    print(f"✅ Déjà fait: {url}")
                    continue
                try:
                    data = scrape_url(driver, url)
                    writer.writerow(data)
                    print(f"✅ Terminé ({i + 1}/{len(urls)})")
                except Exception as e:
                    print(f"❌ Erreur: {e}")
                    continue
        driver.quit()

if __name__ == "__main__":
    main()
