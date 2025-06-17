import requests
import time
from seleniumbase import Driver
from bs4 import BeautifulSoup

root_url = "https://www.immoweb.be/en"
apartments_sales = "https://www.immoweb.be/en/search/apartment/for-sale"
house_sales = "search/house/for-sale"

"""
Check if there is a Captcha. If yes, click manually.
"""
try:
    req_houses = requests.get(house_sales)
    if req_houses.status_code == 200:
        print("House_sales link is okay")
    else:
        raise Exception(f"Status error: {req_houses.status_code}")
except Exception as e:
    print(f"Request failed: {e}")
    driver = Driver(uc=True, headless=True)
    driver.uc_open_with_reconnect(apartments_sales, reconnect_time=6)
    driver.uc_gui_click_captcha()
    # driver.quit()

try:
    driver
except NameError:
    driver = Driver(uc=True, headless=True)

"""
Creation of the list where we'll put all the links of the properties.
"""
all_links = []

"""
We go through each page.
"""
for page_num in range(1, 334):
    page_url = f"https://www.immoweb.be/en/search/house/for-sale?countries=BE&page={page_num}&orderBy=relevance"
    print(f"\n Scraping page {page_num}: {page_url}")

    try:
        driver.uc_open_with_reconnect(page_url, reconnect_time=6)
        time.sleep(5)

        # Click on cookie button if needed
        try:
            driver.click('button[class*="accept"]')
            time.sleep(1)
        except:
            pass

        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        listings = soup.findAll("a", class_="card__title-link")

        for item in listings:
            href = item.get("href")
            if href:
                if href.startswith("/"):
                    full_url = "https://www.immoweb.be" + href
                else:
                    full_url = href
                if full_url not in all_links:
                    all_links.append(full_url)

    except Exception as e:
        print(f"Issue on page {page_num}: {e}")

        """
        Captcha check
        """
        try:
            driver.uc_gui_click_captcha()
        except:
            print("Captcha non cliquable")


print(f"\nTotal amount of apartments found: {len(all_links)}")
for link in all_links:
    print(link)


with open("immoweb_houses_links.txt", "w") as f:
    for link in all_links:
        f.write(link + "\n")

