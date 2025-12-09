from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time

from .db_utils import save_products




URL = "https://www.tiendamonge.com/computadoras"  # o la categoría que usen


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
            # Subir a un contenedor (primero intentamos li, si no, div)
            try:
                container = btn.find_element(By.XPATH, "./ancestor::li[1]")
            except Exception:
                container = btn.find_element(By.XPATH, "./ancestor::div[1]")

            # 1) Título: primer enlace de texto dentro del contenedor
            title_el = container.find_element(
                By.XPATH,
                ".//a[normalize-space()!='' and not(normalize-space()='COMPRAR')]"
            )
            title = title_el.text.strip()

            # 2) Precio: algún nodo dentro del contenedor que tenga el símbolo ₡
            price_el = container.find_element(
                By.XPATH,
                ".//*[contains(text(),'₡')]"
            )
            price_text = price_el.text.strip()

            # Limpiamos el precio dejando solo dígitos y punto
            digits = "".join(ch for ch in price_text if ch.isdigit() or ch == ".")
            price = float(digits) if digits else None

            # 3) URL del producto
            url = title_el.get_attribute("href") or URL

            products.append({
                "title": title,
                "price": price,
                "url": url
            })

        except Exception as e:
            # Si un producto falla, seguimos con el siguiente
            # (si quieres debug, puedes imprimir e)
            continue

    driver.quit()
    print("Productos encontrados en Monge:", len(products))
    return products


def main():
    products = scrape_monge()
    save_products(products)
    print(f"[MONGE] Guardados {len(products)} productos en la BD")


if __name__ == "__main__":
    main()
