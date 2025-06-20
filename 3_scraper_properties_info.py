import requests
from bs4 import BeautifulSoup
import time
import random
import csv
import wakepy

INPUT_FILE = "urls.txt"
OUTPUT_FILE = "output.csv"

property_info = {
        "price": None,
        "type_of_property": None,
        "subtype": None,
        "type_of_sale": None,
        "land_surface": None,
        "living_surface": None,
        "postal_code": None,
        "locality": None,
        "bedrooms": None,
        "description": None,
        "equiped_kitchen": None,
        "plot_surface": None,
        "terrace": None,
        "terrace_surface": None,
        "furnished": None,
        "open_fire": None,
        "garden": None,
        "garden_surface": None,
        "number_of_facades": None,
        "swimming_pool": None,
        "state_of_building": None
    }


def get_random_headers():
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
    ]
    accept_languages = ["en-US,en;q=0.9", "fr-FR,fr;q=0.9,en;q=0.8", "nl-BE,nl;q=0.9,en;q=0.8"]

    headers = {
        "User-Agent": random.choice(user_agents),
        "Accept-Language": random.choice(accept_languages),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }
    return headers


def get_page_html(url):
    headers = get_random_headers()
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    return response.text


def parser(html, url):
    soup = BeautifulSoup(html, "html.parser")
    property_info = {
        "url": url,
        "price": None,
        "type_of_property": None,
        "subtype": None,
        "type_of_sale": None,
        "land_surface": None,
        "living_surface": None,
        "postal_code": None,
        "locality": None,
        "bedrooms": None,
        "description": None,
        "equiped_kitchen": None,
        "plot_surface": None,
        "terrace": None,
        "terrace_surface": None,
        "furnished": None,
        "open_fire": None,
        "garden": None,
        "garden_surface": None,
        "number_of_facades": None,
        "swimming_pool": None,
        "state_of_building": None
    }


    price_tag = soup.find("p", class_="classified__price")
    if price_tag:
        property_info["price"] = price_tag.get_text(strip=True)


    address_tag = soup.find("span", class_="classified__information--address-row")
    if address_tag:
        parts = [t.strip() for t in address_tag.find_all(string=True, recursive=False) if t.strip()]
        if len(parts) >= 2:
            property_info["postal_code"] = parts[0]
            property_info["locality"] = parts[1]


    info_tag = soup.find("p", class_="classified__information--property")
    if info_tag:
        texts = list(info_tag.stripped_strings)
        for text in texts:
            if "bedroom" in text.lower():
                property_info["bedrooms"] = text
            elif "m²" in text or "square meter" in text.lower():
                property_info["living_surface"] = text


    desc_tag = soup.find("meta", attrs={"itemprop": "description"})
    if desc_tag:
        property_info["description"] = desc_tag.get("content", "").strip()


    for script in soup.find_all("script"):
        if "window.dataLayer.push" in script.text and "classified" in script.text:
            json_text = re.search(r"window\.dataLayer\.push\((\{.*?\})\);", script.text, re.DOTALL)
            if json_text:
                try:
                    data = json.loads(json_text.group(1))
                    classified = data.get("classified", {})

                    property_info["type_of_property"] = classified.get("type")
                    property_info["subtype"] = classified.get("subtype")
                    property_info["type_of_sale"] = classified.get("transactionType")
                    property_info["land_surface"] = classified.get("land", {}).get("surface")
                    property_info["plot_surface"] = property_info["land_surface"]
                    property_info["equiped_kitchen"] = classified.get("kitchen", {}).get("type")
                    property_info["terrace"] = classified.get("outdoor", {}).get("terrace", {}).get("exists")
                    property_info["garden"] = classified.get("outdoor", {}).get("garden", {}).get("exists")
                    property_info["garden_surface"] = classified.get("outdoor", {}).get("garden", {}).get("surface")
                    property_info["swimming_pool"] = classified.get("wellnessEquipment", {}).get("hasSwimmingPool")
                    property_info["state_of_building"] = classified.get("building", {}).get("condition")
                    property_info["number_of_facades"] = classified.get("facadeCount") or classified.get("facade_count")

                except Exception as e:
                    print("Échec du parsing JSON : ", e)
            break

    return property_info




"""def parser(html, url):
    soup = BeautifulSoup(html, "html.parser")

    # Price
    price_tag = soup.find("p", class_="classified__price")
    if price_tag:
        price = price_tag.get_text(strip=True)


    # Bedrooms & surface
    info_tag = soup.find("p", class_="classified__information--property")
    if info_tag:
        texts = [t.strip() for t in info_tag.stripped_strings if t.strip()]
        if "bedroom" in texts[0].lower():
            property_info["bedrooms"] = texts[0]
        for text in texts:
            if "m²" in text or "square meter" in text.lower():
                property_info["living_surface"] = text
            elif text.isdigit():
                property_info["living_surface"] = text + " m²"


    # Kitchen equipped
    kitchen_tag = soup.find("td", class_="classified-table__data")
    if kitchen_tag:
        property_info["equiped_kitchen"] = kitchen_tag.get_text(strip=True)

    # Postal code and locality
    address_tag = soup.find("span", class_="classified__information--address-row")
    if address_tag:
        texts = [t.strip() for t in address_tag.find_all(string=True, recursive=False) if t.strip()]
        if len(texts) >= 2:
            property_info["postal_code"] = texts[0]
            property_info["locality"] = texts[1]

    # Description
    desc_tag = soup.find("meta", attrs={"itemprop": "description"})
    if desc_tag:
        property_info["description"] = desc_tag.get("content", "").strip()



    # Plot surface
    plot_surface_tag = soup.find("td", class_="classified-table__data")
    if plot_surface_tag:
        property_info[plot_surface]= plot_surface_tag

    return property_info
"""

def save_csv(data_list):
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=property_info)
        writer.writeheader()
        for row in data_list:
            writer.writerow(row)


def main():
    with open(INPUT_FILE, "r") as f:
        urls = [line.strip() for line in f if line.strip()]

    all_data = []

    with wakepy.keep.running():
        total = len(urls)
        for i, url in enumerate(urls, 1):
            print(f"({i}/{total}) Scraping: {url}")
            try:
                html = get_page_html(url)
                data = parser(html, url)
                print(f"✅ Données extraites pour {url}")
            except Exception as e:
                print(f"❌ Erreur pour {url}: {e}")
                data = dict.fromkeys(property_info, "")
                data["url"] = url
            all_data.append(data)

            time.sleep(random.uniform(0.5, 3.5)) 

    save_csv(all_data)
    print("🎉 Scraping terminé. Données sauvegardées dans", OUTPUT_FILE)


if __name__ == "__main__":
    main()
