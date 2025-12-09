import psycopg2
import os

#guarda productos en la base de datos
def save_products(products):
    conn = psycopg2.connect(
        host="localhost",
        port=5434,
        user="admin",
        password="admin",
        database="scrapingdb"
    )
    cursor = conn.cursor()
  #Inserta productos en la tabla products
    query = """
        INSERT INTO products (title, price, url)
        VALUES (%s, %s, %s);
    """
#Recorre la lista de productos y los inserta en la base de datos
    for p in products:
        cursor.execute(query, (
            p["title"],
            p.get("price"),
            p.get("url")
        ))

    conn.commit()
    cursor.close()
    conn.close()

def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5434"),
        user=os.getenv("DB_USER", "admin"),
        password=os.getenv("DB_PASSWORD", "admin"),
        database=os.getenv("DB_NAME", "scrapingdb")
    )