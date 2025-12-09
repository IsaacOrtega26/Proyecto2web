# Proyecto Web Scraping con Docker – Tienda Monge + BooksToScrape

Proyecto desarrollado para el curso **Tecnologías y Sistemas Web III**, cuyo objetivo es construir un sistema de **Web Scraping**, tanto **estático** como **dinámico**, almacenar los datos en una base de datos PostgreSQL, exponerlos mediante una API y visualizar resultados en un dashboard web.

Además, toda la infraestructura se ejecuta en **Docker** mediante `docker-compose`.


# Contenidos

1. Arquitectura general  
2. Diagrama del sistema  
3. Estructura del proyecto  
4. Base de datos  
5. Configuración de conexión (variables de entorno)  
6. Instalación local  
7. Ejecución del proyecto  
8. Scraping estático (BooksToScrape)  
9. Scraping dinámico (Tienda Monge)  
10. Scheduler  
11. Dashboard  
12. Uso con Docker  
13. Comandos útiles  
14. Mejoras futuras  

---

# 1️ Arquitectura General

El sistema consiste en:

- **Scraper estático**  
  Obtiene información del sitio *BooksToScrape*.

- **Scraper dinámico**  
  Usa Selenium para extraer productos reales desde:
https://www.tiendamonge.com/computadoras

markdown


- **Base de datos PostgreSQL**  
Almacena productos registrados por los scrapers.

- **API REST con Flask**  
Expone los productos en formato JSON.

- **Dashboard web**  
Tabla interactiva con filtros, ordenamiento y enlaces.

- **Scheduler (APScheduler)**  
Ejecuta el scraping cada cierto intervalo en automático.

- **Docker Compose**  
Orquesta los servicios:
- DB
- pgAdmin
- API
- Scheduler

---

# 2 Base de Datos
Tabla utilizada:

CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    price NUMERIC(10, 2),
    url TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

# 3 Conexión a la Base de Datos
Usamos variables de entorno, con valores por defecto (modo local):

def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5434"),
        user=os.getenv("DB_USER", "admin"),
        password=os.getenv("DB_PASSWORD", "admin"),
        database=os.getenv("DB_NAME", "scrapingdb"),
    )

En Docker, docker-compose.yml configura:

DB_HOST=db
DB_PORT=5432

# 4 Instalación Local
Crear entorno virtual:
python -m venv venv
venv\Scripts\activate
Instalar dependencias:
css
pip install -r requirements.txt

## requirements.txt incluye:
flask
psycopg2-binary
apscheduler
selenium
webdriver-manager
requests
beautifulsoup4

# 5 Ejecución Local
1. Levantar base de datos (Docker requerido):
docker compose up -d db pgadmin

2. Ejecutar scrapers manualmente:
python scrapper/scraper_static.py
python -m scrapper.scrapper_dynamic

3. Iniciar el scheduler:
python scheduler.py

4. Iniciar API Flask:
python api/json_api_server.py

## Rutas disponibles:
Dashboard → http://localhost:5000

API JSON → http://localhost:5000/results

# 6 Scraper Estático (BooksToScrape)
scrapper/scraper_static.py

## Características:
- Uso de requests
- HTML parseado con BeautifulSoup
- Obtiene título, precio y URL
- Guarda en BD vía save_products()

# 7 Scraper Dinámico (Tienda Monge)
scrapper/scrapper_dynamic.py

## Características:

- Selenium headless + webdriver-manager
- Limpieza de texto para extraer precio real
- Títulos sin contaminar con “COMPRAR” o precios
- Obtiene enlace real al producto
- Guarda en BD

# 8 Scheduler
scheduler.py

## Funciones:
- Ejecuta scraping inicial (ambos sitios)
- Programa scraping recurrente (por defecto cada 30 min)
- Corre dentro de un contenedor Docker independiente

# 9 Dashboard
HTML dinámico con JavaScript:
- Tabla de productos
- Filtro por texto
- Rango de precios
- Filtro por origen
- Ordenamiento por columnas
- Botón “Ver producto” con link al sitio original

# 10 Uso Completo con Docker
Construir y ejecutar todo el proyecto:
docker compose up -d --build

## Servicios:

- API + Dashboard  http://localhost:5000
- pgAdmin  http://localhost:5050
- Base de datos
- Scheduler automático

## Ver logs del scheduler:
- docker logs -f proyecto2web-scheduler-1

## Detener todo:
- docker compose down

## Borrar base de datos (volumen):
- docker compose down -v

# 11 Comandos Útiles
Ver contenedores:
- docker compose ps

## Reconstruir únicamente imagen app:
- docker compose build app

## Ejecutar scrapers dentro del contenedor:
- docker exec -it proyecto2web-scheduler-1 bash