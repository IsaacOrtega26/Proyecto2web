# scrapper/scraper_static.py

import requests
from bs4 import BeautifulSoup
import re
from .db_utils import save_products

# URL del sitio estático de ejemplo
URL = "https://books.toscrape.com/"

# Función para realizar el scraping
def scrape_books():
    resp = requests.get(URL)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    products = []

    # Cada libro está dentro de un contenedor con clase product_pod
    for item in soup.select(".product_pod"):
        title = item.h3.a["title"]
        price_text = item.select_one(".price_color").text.strip()

        # Limpiar caracteres no numéricos (símbolo de moneda, etc.)
        price_clean = re.sub(r"[^0-9.]", "", price_text)

        # Convertir a float
        price = float(price_clean)
        
        # Agregar el producto a la lista
        products.append({
            "title": title,
            "price": price,
            "url": URL
        })

    return products


def main():
    products = scrape_books()
    save_products(products)
    print(f"[BOOKS] Guardados {len(products)} productos en la BD (BooksToScrape)")


if __name__ == "__main__":
    main()
