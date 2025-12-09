# scrapper/scrapper_dynamic.py

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
import re

from .db_utils import save_products  # db_utils.py debe estar dentro de scrapper/

URL = "https://www.tiendamonge.com/computadoras"


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
    time.sleep(5)  # esperar a que cargue bien la página

    print("Título de la página:", driver.title)

    products = []

    # Tomamos los botones "COMPRAR" y desde ahí subimos al contenedor del producto
    buy_buttons = driver.find_elements(
        By.XPATH,
        "//a[normalize-space()='COMPRAR']"
    )
    print("Botones COMPRAR encontrados:", len(buy_buttons))

    for btn in buy_buttons:
        try:
            # Subir al contenedor principal del producto
            try:
                container = btn.find_element(By.XPATH, "./ancestor::li[1]")
            except Exception:
                container = btn.find_element(By.XPATH, "./ancestor::div[1]")

            # ====== LINK + TÍTULO DEL PRODUCTO ======
            # buscamos el primer <a> que NO sea el botón COMPRAR
            try:
                link_el = container.find_element(
                    By.XPATH,
                    ".//a[normalize-space()!='' and normalize-space()!='COMPRAR'][1]"
                )
            except Exception:
                link_el = None

            title = ""

            if link_el is not None:
                # probar primero atributo title, luego el texto
                title = (link_el.get_attribute("title") or link_el.text or "").strip()

            # si aún está vacío, usamos texto del contenedor como respaldo
            if not title:
                full_text = container.text.strip()
                title = full_text.split("\n")[0] if full_text else "Producto Monge"

            # --- LIMPIAR TÍTULO: quitar precios y la palabra COMPRAR ---
            # cortar desde el primer símbolo de colones (para evitar meter el precio en el título)
            title_clean = re.split(r"₡|¢", title)[0]
            title_clean = title_clean.replace("COMPRAR", "").strip()

            # ====== PRECIO ======
            price = None
            try:
                price_el = container.find_element(
                    By.XPATH,
                    ".//*[contains(text(),'₡') or contains(text(),'¢')]"
                )
                price_text = price_el.text.strip()
                # Para colones usamos los dígitos SOLAMENTE (43.495 -> 43495)
                digits = "".join(ch for ch in price_text if ch.isdigit())
                if digits:
                    price = int(digits)
            except Exception:
                pass

            # ====== URL DEL PRODUCTO ======
            url = URL
            if link_el is not None:
                href = link_el.get_attribute("href")
                if href:
                    url = href

            products.append({
                "title": title_clean,
                "price": price,
                "url": url,
            })

        except Exception:
            # Si algo truena con un producto, seguimos con el siguiente
            continue

    driver.quit()
    print("Productos encontrados en Monge:", len(products))
    return products


def main():
    print("[MONGE] Iniciando scraping dinámico...")
    products = scrape_monge()
    print("[MONGE] Productos obtenidos:", len(products))
    save_products(products)
    print(f"[MONGE] Guardados {len(products)} productos en la BD")


if __name__ == "__main__":
    main()
