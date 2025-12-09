from apscheduler.schedulers.blocking import BlockingScheduler
from scrapper.scraper_static import main as run_static_scraper
from scrapper.scrapper_dynamic import main as run_dynamic_scraper

scheduler = BlockingScheduler()

print("Ejecutando scraping inicial...")
run_static_scraper()
run_dynamic_scraper()

scheduler.add_job(run_static_scraper, "interval", minutes=30)
scheduler.add_job(run_dynamic_scraper, "interval", minutes=30)

print("Scheduler iniciado. Presiona Ctrl+C para detenerlo.")
scheduler.start()
