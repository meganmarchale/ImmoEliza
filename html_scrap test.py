import time
import requests
from fake_useragent import UserAgent
from pathlib import Path
from wakepy import keep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

TIMEOUT = 2
INPUT_FILE = "urls.txt"
OUTPUT_FOLDER = Path("html_pages_")
OUTPUT_FOLDER.mkdir(exist_ok=True)

def get_random_user_agent():
    try:
        return UserAgent().random
    except:
        return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/125 Safari/537.36"

def extract_text(driver, selector):
    try:
        element = WebDriverWait(driver, TIMEOUT).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
        )
        return element.text.strip()
    except:
        return ""

def create_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(f"--user-agent={get_random_user_agent()}")
    return webdriver.Chrome(options=options)

def download_html(driver, url, index):
    try:
        print(f"🔗 ({index}) Loading: {url}")
        driver.get(url)
        time.sleep(5)
        html = driver.page_source
        file_path = OUTPUT_FOLDER / f"page_{index}.html"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"✅ Saved: {file_path.name}")
    except Exception as e:
        print(f"❌ Failed to load {url}: {e}")

def main():
    with open(INPUT_FILE, "r") as f:
        urls = [line.strip() for line in f if line.strip()]

    with keep.running():
        driver = create_driver()
        for idx, url in enumerate(urls, 1):
            download_html(driver, url, idx)
            time.sleep(3)
        driver.quit()

if __name__ == "__main__":
    main()
