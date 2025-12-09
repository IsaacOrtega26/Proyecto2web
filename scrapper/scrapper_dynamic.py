from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time

from .db_utils import save_products




URL = "https://www.tiendamonge.com/televisores"  # o la categoría que usen


def scrape_monge():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    driver.get(URL)
    time.sleep(5)  # esperar a que cargue

    products = []

    # TODO: ajustar selectores con el inspector de Monge
    cards = driver.find_elements(By.CSS_SELECTOR, ".product-card, .vtex-product-summary-2-x-container")
    for card in cards:
        try:
            title_el = card.find_element(By.CSS_SELECTOR, "h3, .product-name, .vtex-product-summary-2-x-productBrand")
            price_el = card.find_element(By.CSS_SELECTOR, ".price, .vtex-product-price-1-x-sellingPriceValue")

            title = title_el.text.strip()
            price_text = price_el.text.strip()

            digits = "".join(ch for ch in price_text if ch.isdigit() or ch == ".")
            price = float(digits) if digits else None

            try:
                link_el = card.find_element(By.CSS_SELECTOR, "a")
                url = link_el.get_attribute("href")
            except Exception:
                url = URL

            products.append({
                "title": title,
                "price": price,
                "url": url,
            })
        except Exception:
            continue

    driver.quit()
    return products


def main():
    products = scrape_monge()
    save_products(products)
    print(f"[MONGE] Guardados {len(products)} productos en la BD")


if __name__ == "__main__":
    main()
