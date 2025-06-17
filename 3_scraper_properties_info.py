import requests
from bs4 import BeautifulSoup
import time
import json

"""
with open("all_links_cleaned.txt", "r") as file:
    for link in file:
        requests.get(link)
"""

# Try on the first link first !
url = "https://www.immoweb.be/en/classified/exceptional-property/for-sale/woluwe-saint-pierre/1150/20730828"

response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

locality = soup.getText("div.classified__information--address")
type = soup.getText("h1.classified__title")
price = soup.getText("span.classified__price")

# Détails du bien : liste d’infos sous forme de <li>
details = soup.select("li.classified__list--item")
#for detail in details:

print(soup)
print(locality)
print(type)
print(price)


