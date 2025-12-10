from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
import re

from .db_utils import save_products
# URL del sitio dinámico de Tienda Monge
URL = "https://www.tiendamonge.com/computadoras"

# Función para realizar el scraping dinámico
def scrape_monge():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

# Iniciar el navegador Chrome en modo headless
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    driver.get(URL)
    time.sleep(5)  # espera a que cargue bien la página

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

            # Buscar el enlace del producto para obtener el título
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

            # cortar desde el primer símbolo de colones (para evitar meter el precio en el título)
            title_clean = re.split(r"₡|¢", title)[0]
            title_clean = title_clean.replace("COMPRAR", "").strip()

            # Precio
            price = None
            try:
                price_el = container.find_element(
                    By.XPATH,
                    ".//*[contains(text(),'₡') or contains(text(),'¢')]"
                )
                price_text = price_el.text.strip()

                # Para colones usamos solo dígitos
                digits = "".join(ch for ch in price_text if ch.isdigit())
                if digits:
                    price = int(digits)
            except Exception:
                pass

            # URL del producto
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

# Función principal para ejecutar el scraper dinámico
def main():
    print("[MONGE] Iniciando scraping dinámico...")
    products = scrape_monge()
    print("[MONGE] Productos obtenidos:", len(products))
    save_products(products)
    print(f"[MONGE] Guardados {len(products)} productos en la BD")


if __name__ == "__main__":
    main()
