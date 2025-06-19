from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import random

def random_user_agent():
    ua_list = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/125 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_2_1) AppleWebKit/537.36 Chrome/124 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/123 Safari/537.36",
    ]
    return random.choice(ua_list)

with sync_playwright() as p:
    # Démarre Chromium avec interface visible (non headless)
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    url = "https://immovlan.be/fr/immobilier?transactiontypes=a-vendre,en-vente-publique&noindex=1"
    url2 = "https://www.immoweb.be/fr/recherche/maison-et-appartement/a-vendre?countries=BE&page=1&orderBy=newest"
    url3 = "https://www.zimmo.be/fr/recherche/a-vendre/?pagina=2&sort_order=DESC&sort=RANKING_SCORE#gallery"

    # Aller sur la page Immoweb
    page.goto(url2)

    page.wait_for_timeout(1000)

    # Récupère le HTML rendu
    html = page.content()
    print(html[:2000])

    """
    soup = BeautifulSoup(html, "html.parser")
    section = soup.find("section", id="search-results")
    articles = section.find_all("article")
    articles = [article for article in articles if (article.get("class") != None) ]
    browser.close()

    print("=" * 40)
    for i, article in enumerate(articles):
        print(f"--- Article {i+1} ---")
        print(article.get("class"))
        print(article.text.strip()[:150])
        print("=" * 40)
    print(f"{len(articles)} articles trouvés.")
    
    """
    