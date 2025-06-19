import scrapy 
from scrapy_splash import SplashRequest 
 
class MySpider(scrapy.Spider): 
 name = 'my_spider' 
 
def start_requests(self): 
yield SplashRequest(url="https://www.immoweb.be/en/classified/house/for-sale/kraainem/1950/20821483", callback=self.parse) 
 

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
 
yield { 
'data': data 
 } 
