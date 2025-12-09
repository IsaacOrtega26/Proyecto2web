import requests
from bs4 import BeautifulSoup
import re

from .db_utils import save_products



URL = "https://books.toscrape.com/"

def scrape_books():
    resp = requests.get(URL)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    products = []

    for item in soup.select(".product_pod"):
        title = item.h3.a["title"]
        price_text = item.select_one(".price_color").text.strip()

        price_clean = re.sub(r"[^0-9.]", "", price_text)
        price = float(price_clean)

        products.append({
            "title": title,
            "price": price,
            "url": URL
        })

    return products

def main():
    products = scrape_books()
    save_products(products)
    print(f"Guardados {len(products)} productos en la BD")

if __name__ == "__main__":
    main()
