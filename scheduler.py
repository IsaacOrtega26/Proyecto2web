from apscheduler.schedulers.blocking import BlockingScheduler
from scrapper.scraper_static import main as run_static_scraper
from scrapper.scrapper_dynamic import main as run_dynamic_scraper

def main():
    scheduler = BlockingScheduler()

    print("Ejecutando scraping inicial...")
    run_static_scraper()
    run_dynamic_scraper()

    # Recorre cada 30 minutos, se puede ajustar al valor que uno desee
    scheduler.add_job(run_static_scraper, "interval", minutes=30)
    scheduler.add_job(run_dynamic_scraper, "interval", minutes=30)

    print("Scheduler iniciado. Presiona Ctrl+C para detenerlo.")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("Scheduler detenido.")


if __name__ == "__main__":
    main()
