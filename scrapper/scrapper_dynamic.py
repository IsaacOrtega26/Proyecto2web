from time import sleep
from urllib.parse import urljoin
import re
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

# imports al proyecto
from scrapper.db_utils import save_products, find_product_by_title, log_change

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("scrapper_dynamic")

BASE = "https://www.tiendamonge.com"

# Lista de categorías/paths que queremos scrapear 
CATEGORIES = [
    "/computadoras",
    "/celulares",
    "/televisores",
    "/audio",
    "/consolas-y-videojuegos",
    "/electrodomesticos"  
]

# Selectores probables (se prueban en orden hasta que alguno funcione)
CARD_SELECTORS = [
    ".product-card", ".product-item", ".product", ".product-grid-item", "li.product"
]
TITLE_SELECTORS = [
    ".product-title", ".title", "h2", "a.product-name", ".name"
]
PRICE_SELECTORS = [
    ".price", ".product-price", ".price-amount", "span.price"
]
LINK_SELECTORS = [
    "a", "a.product-link"
]
IMAGE_SELECTORS = [
    "img", ".product-image img", "img.product-img"
]


def parse_price(text):
    """Extrae un número float desde texto que contiene símbolos de moneda."""
    if not text:
        return None
    # quitar letras, símbolos y dejar números y punto/coma
    cleaned = re.sub(r"[^\d,.\-]", "", text)
    # normalizar coma decimal a punto si corresponde (ej: "1.234,56")
    if cleaned.count(",") == 1 and cleaned.count(".") > 0:
        # probable formato 1.234,56 -> quitar puntos y cambiar coma por punto
        cleaned = cleaned.replace(".", "").replace(",", ".")
    elif cleaned.count(",") > 1 and cleaned.count(".") == 0:
        cleaned = cleaned.replace(",", "")
    cleaned = cleaned.replace(",", ".")
    try:
        return float(cleaned)
    except:
        return None


def get_driver():
    opts = Options()
    opts.add_argument("--headless=new")  # usar nueva opción headless si disponible
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    # opcional: user-agent
    opts.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115 Safari/537.36")
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=opts)
    driver.set_page_load_timeout(30)
    return driver


def first_element_text(card, selectors):
    """Intenta varios selectores dentro de un elemento y devuelve texto limpio."""
    for sel in selectors:
        try:
            el = card.find_element(By.CSS_SELECTOR, sel)
            txt = el.text.strip()
            if txt:
                return txt
        except NoSuchElementException:
            continue
    return None


def first_element_attr(card, selectors, attr="href"):
    """Intenta varios selectores y devuelve un atributo (href/src)."""
    for sel in selectors:
        try:
            el = card.find_element(By.CSS_SELECTOR, sel)
            val = el.get_attribute(attr)
            if val:
                return val
        except NoSuchElementException:
            continue
    return None


def scrape_category(driver, category_path, max_pages=5, sleep_between_pages=1.0):
    """
    Recorre las páginas de una categoría y devuelve lista de productos.
    max_pages: límite para no raspar todo el sitio en pruebas.
    """
    products = []
    page = 1
    category_url = urljoin(BASE, category_path)
    logger.info(f"Scrapeando categoría: {category_url}")

    while page <= max_pages:
        url = f"{category_url}?page={page}"
        try:
            driver.get(url)
        except TimeoutException:
            logger.warning(f"Timeout cargando {url}, intentando de nuevo...")
            driver.get(url)
        sleep(0.5)

        # intentar localizar cards
        cards = []
        for sel in CARD_SELECTORS:
            cards = driver.find_elements(By.CSS_SELECTOR, sel)
            if cards:
                break

        # si no hay cards, intentamos detectar productos en otro contenedor
        if not cards:
            anchors = driver.find_elements(By.CSS_SELECTOR, "a")
            product_links = []
            for a in anchors:
                href = a.get_attribute("href") or ""
                if "/producto/" in href or "/productos/" in href:
                    product_links.append(href)
            product_links = list(dict.fromkeys(product_links))
            for pl in product_links:
                # crear entrada provisional
                products.append({"title": None, "price": None, "url": pl, "image_url": None})
            if product_links:
                break

        for card in cards:
            # título
            title = first_element_text(card, TITLE_SELECTORS)
            # precio
            price_text = first_element_text(card, PRICE_SELECTORS)
            price = parse_price(price_text)
            # link relativo/absoluto
            href = None
            try:
                # intentar anchor directo
                a = card.find_element(By.CSS_SELECTOR, "a")
                href = a.get_attribute("href")
            except NoSuchElementException:
                href = first_element_attr(card, LINK_SELECTORS, "href")

            url_full = urljoin(BASE, href) if href else None

            # imagen
            img = first_element_attr(card, IMAGE_SELECTORS, "src")
            img_full = urljoin(BASE, img) if img else None

            product = {
                "title": title or "Sin título",
                "price": price,
                "url": url_full,
                "image_url": img_full
            }
            products.append(product)

        
        next_found = False
        try:
            # muchos sitios usan rel="next"
            nxt = driver.find_element(By.CSS_SELECTOR, "a[rel='next']")
            if nxt and nxt.is_displayed():
                next_found = True
        except NoSuchElementException:
            # buscar enlace con texto siguiente
            try:
                nxt2 = driver.find_element(By.XPATH, "//a[contains(translate(text(),'S','s'),'siguiente') or contains(text(),'»') or contains(text(),'Next')]")
                if nxt2:
                    next_found = True
            except NoSuchElementException:
                next_found = False

        if not next_found:
            break

        page += 1
        sleep(sleep_between_pages)

    logger.info(f"Encontrados {len(products)} productos en {category_path} (paginas escaneadas: {page})")
    return products


def scrape_all(max_pages_per_category=3):
    driver = get_driver()
    all_products = []
    try:
        for cat in CATEGORIES:
            try:
                prods = scrape_category(driver, cat, max_pages=max_pages_per_category)
                all_products.extend(prods)
            except Exception as e:
                logger.error(f"Error scrappeando {cat}: {e}")
    finally:
        driver.quit()
    # deduplicar por URL (si hay)
    seen = set()
    unique = []
    for p in all_products:
        key = (p.get("url") or p.get("title"))
        if key and key not in seen:
            seen.add(key)
            unique.append(p)
    return unique

from scrapper.db_utils import save_products, find_product_by_title, log_change, delete_missing_products
def main():
    logger.info("Iniciando scraper dinámico (Monge) — recolectando productos...")
    products = scrape_all(max_pages_per_category=2)  

    scraped_urls = [p["url"] for p in products if p.get("url")]
    delete_missing_products(scraped_urls)

    if not products:
        logger.info("No se obtuvieron productos.")
        return {"inserted": 0, "updated": 0}

    # Guardar en BD a través de save_products 
    try:
        save_products(products)
        log_change(f"Scraper dinámico: guardados {len(products)} productos")
        return {"inserted": len(products), "updated": 0}
    except Exception as e:
        logger.error("Error guardando productos en BD: %s", e)
        log_change(f"ERROR guardando productos dinámicos: {e}")
        return {"inserted": 0, "updated": 0}


if __name__ == "__main__":
    main()
