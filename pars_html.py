import requests

def get_random_user_agent():
    headers =  {
        'User-Agent': (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) '
            'Gecko/20100101 Firefox/115.0'
        ),
        'Accept': (
            'text/html,application/xhtml+xml,application/xml;q=0.9,'
            'image/avif,image/webp,*/*;q=0.8'
        ),
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'TE': 'trailers',
    }

    response = requests.get(url, headers=headers)
    return response

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

url = "https://www.immoweb.be/en/classified/new-real-estate-project-houses/for-sale/bavikhove/8531/20818783"
resp = requests.get(url, headers={
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
})
with open("test_immoweb.html", "w", encoding="utf-8") as f:
    f.write(resp.text)
print("HTML enregistré")
