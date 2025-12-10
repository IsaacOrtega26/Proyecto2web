from apscheduler.schedulers.blocking import BlockingScheduler
from scrapper.scraper_static import main as run_static_scraper
from scrapper.scrapper_dynamic import main as run_dynamic_scraper
from datetime import datetime
import os
from scrapper.scrapper_dynamic import main as run_dynamic_scraper
from scrapper.downloader import process_files  


LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "changes.log")

def ensure_log_dir():
    os.makedirs(LOG_DIR, exist_ok=True)

def log_change(message: str):
    """Añade una línea al log con timestamp."""
    ensure_log_dir()
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now().isoformat()} - {message}\n")
    print("LOG:", message)  # útil en consola/docker logs

# Wrappers para ejecutar y registrar cada scraper
def run_and_log_static():
    log_change("Iniciando scraper estático (BooksToScrape).")
    try:
        run_static_scraper()
        log_change("Scraper estático finalizado correctamente.")
    except Exception as e:
        log_change(f"ERROR en scraper estático: {e}")

def run_and_log_dynamic():
    log_change("Iniciando scraper dinámico (Tienda Monge).")
    try:
        run_dynamic_scraper()
        log_change("Scraper dinámico finalizado correctamente.")
    except Exception as e:
        log_change(f"ERROR en scraper dinámico: {e}")

def main():
    scheduler = BlockingScheduler()

    print("Ejecutando scraping inicial...")
    # Ejecuta ambos scrapers al arrancar y los registra en logs
    run_and_log_static()
    run_and_log_dynamic()

    # Agrega trabajos periódicos 
    scheduler.add_job(run_dynamic_scraper, "interval", minutes=30, id="static_scraper")
    scheduler.add_job(process_files, "interval", minutes=30, id="dynamic_scraper")


    log_change("Scheduler iniciado. Jobs: static_scraper (30m), dynamic_scraper (30m).")

    print("Scheduler iniciado. Presiona Ctrl+C para detenerlo.")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        log_change("Scheduler detenido por KeyboardInterrupt/SystemExit.")
        print("Scheduler detenido.")

if __name__ == "__main__":
    main()
