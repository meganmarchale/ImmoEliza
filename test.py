import csv
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fake_useragent import UserAgent
from wakepy import keep


INPUT_FILE = "urls.txt"
OUTPUT_FILE = "results__.csv"
TIMEOUT = 5  # secondes
WAIT_BETWEEN_REQUESTS = (2, 4)  

FIELDNAMES = [
    "url", "title", "price", "property_type", "subtype", "postal_code",
    "bedrooms", "surface", "condition", "kitchen", "terrace",
    "terrace_surface", "land_surface", "agency_name"
]


def get_random_user_agent():
    return UserAgent().random

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



def scrape(url, driver):
    data = {key: "" for key in FIELDNAMES}
    data["url"] = url

    try:
        driver.get(url)

        WebDriverWait(driver, TIMEOUT).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        data["title"] = driver.title or "immoweb.be"

        data["price"] = extract_text(driver, "#classified-header > div > div > div.grid__item.desktop--9 > div > div.classified__header-primary-info > p > span:nth-child(1)") #selector path
        data["surface"] = extract_text(driver, "//*[@id="accordion_5f72cb3c-c9e4-4ee4-9cf7-aaa91f0ea62e"]/table/tbody/tr[1]/td/text()") #xpath
        data["bedrooms"] = extract_text(driver, "#accordion_855450bd-c22b-420d-9e2a-807bcb2f307e > table > tbody > tr:nth-child(3) > td")
        data["kitchen"] = extract_text(driver, "#accordion_255886b2-0677-46b1-8eb1-94a501b3bf22 > table > tbody > tr:nth-child(3) > td")
        data["condition"] = extract_text(driver, "#accordion_c9fcfeed-9870-4eb1-99c7-5bfd4310e821 > table > tbody > tr:nth-child(2) > td")
        data["land_surface"] = extract_text(driver, "#accordion_d6ff9f0a-38d0-4d3c-8093-da0367891644 > table > tbody > tr:nth-child(1) > td")
        data["terrace"] = "yes" if "Terrace" in driver.page_source else "no"
        data["property_type"] = "new_project"
        data["subtype"] = url.split("/")[5] if len(url.split("/")) > 5 else ""
        data["postal_code"] = url.split("/")[6] if len(url.split("/")) > 6 else ""

    except Exception as e:
        print(f"Erreur pour {url}: {e}")

    return data


def main():
    with open(INPUT_FILE, "r") as f:
        urls = [line.strip() for line in f if line.strip()]

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES)
        writer.writeheader()

        driver = create_driver()

        with keep.running():
            for idx, url in enumerate(urls):
                print(f"({idx+1}/{len(urls)}) Scraping: {url}")
                data = scrape(url, driver)
                writer.writerow(data)
                time.sleep(random.uniform(*WAIT_BETWEEN_REQUESTS))

        driver.quit()

if __name__ == "__main__":
    main()
