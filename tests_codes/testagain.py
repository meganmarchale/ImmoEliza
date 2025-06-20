import csv
import time
import random
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from wakepy import keep

# Configuration
INPUT_FILE = "urls.txt"
OUTPUT_FILE = "output.csv"
FIELDS = [
    "url", "title", "price", "property_type", "subtype", "postal_code",
    "bedrooms", "surface", "condition", "kitchen", "terrace",
    "terrace_surface", "land_surface", "agency_name"
]

# User-Agents pool
USER_AGENTS = [
    # Add more if needed
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36",
]

def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument(f"user-agent={random.choice(USER_AGENTS)}")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    return webdriver.Chrome(options=chrome_options)

def safe_xpath_text(driver, xpath):
    try:
        return driver.find_element(By.XPATH, xpath).text.strip()
    except:
        return ""

def scrape_page(driver, url):
    driver.get(url)
    time.sleep(random.uniform(2.5, 4.5))  # simulate human

    data = {field: "" for field in FIELDS}
    data["url"] = url

    # 1. Try structured JSON-LD
    try:
        json_ld = driver.find_element(By.XPATH, '//script[@type="application/ld+json"]').get_attribute('innerHTML')
        parsed = json.loads(json_ld)
        if isinstance(parsed, list):
            parsed = parsed[0]

        data["title"] = parsed.get("name", "")
        data["price"] = parsed.get("offers", {}).get("price", "")
        data["postal_code"] = parsed.get("address", {}).get("postalCode", "")
        data["property_type"] = parsed.get("@type", "")
        data["agency_name"] = parsed.get("seller", {}).get("name", "")
    except Exception as e:
        print(f"⚠️ JSON-LD indisponible ou mal formé ({url})")

    # 2. Try visual XPath fallback
    data["bedrooms"] = safe_xpath_text(driver, '//li[contains(text(), "Bedrooms")]')
    data["surface"] = safe_xpath_text(driver, '//li[contains(text(), "Habitable surface")]')
    data["condition"] = safe_xpath_text(driver, '//li[contains(text(), "Building condition")]')
    data["kitchen"] = safe_xpath_text(driver, '//li[contains(text(), "Kitchen")]')
    data["terrace"] = safe_xpath_text(driver, '//li[contains(text(), "Terrace")]')
    data["terrace_surface"] = safe_xpath_text(driver, '//li[contains(text(), "Terrace surface")]')
    data["land_surface"] = safe_xpath_text(driver, '//li[contains(text(), "Land surface")]')
    data["subtype"] = safe_xpath_text(driver, '//li[contains(text(), "Subtype")]')

    return data

def save_csv(data_list):
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        for row in data_list:
            writer.writerow(row)

def main():
    with open(INPUT_FILE, "r") as f:
        urls = [line.strip() for line in f if line.strip()]

    all_data = []
    driver = get_driver()

    with keep.running():  # 👈 Wakepy here
        total = len(urls)
        for i, url in enumerate(urls, 1):
            print(f"🔗 ({i}/{total}) Scraping: {url}")
            try:
                data = scrape_page(driver, url)
                if data["title"] or data["price"]:  # Only keep useful rows
                    print(f"✅ Données récupérées: {data['title']}")
                else:
                    print("⚠️ Données manquantes.")
                all_data.append(data)
            except Exception as e:
                print(f"❌ Erreur pour {url}: {e}")
                all_data.append({field: "" for field in FIELDS} | {"url": url})

    driver.quit()
    save_csv(all_data)
    print("🎉 Scraping terminé.")

if __name__ == "__main__":
    main()
