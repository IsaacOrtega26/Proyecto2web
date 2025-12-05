from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def scrape_dynamic():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)

    driver.get("https://www.tiendamonge.com/")
    
    items = driver.find_elements("css selector", ".product-item")
    
    results = []
    for item in items:
        results.append({
            "title": item.text
        })

    driver.quit()
    return results