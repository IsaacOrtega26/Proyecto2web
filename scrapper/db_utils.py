import os
import psycopg2

#obtiene una conexión a la base de datos
def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5434"),
        user=os.getenv("DB_USER", "admin"),
        password=os.getenv("DB_PASSWORD", "admin"),
        database=os.getenv("DB_NAME", "scrapingdb"),
    )

#guarda productos en la base de datos
def save_products(products):
    if not products:
        print("No hay productos para guardar.")
        return

    conn = get_connection()
    cur = conn.cursor()

    try:
        for p in products:
            title = p.get("title") or "Producto"
            price = p.get("price")
            url = p.get("url")

            cur.execute(
                """
                INSERT INTO products (title, price, url)
                VALUES (%s, %s, %s)
                """,
                (title, price, url),
            )

        conn.commit()
        print(f"Guardados {len(products)} productos en la BD.")
    except Exception as e:
        conn.rollback()
        print("Error guardando productos:", e)
    finally:
        cur.close()
        conn.close()
