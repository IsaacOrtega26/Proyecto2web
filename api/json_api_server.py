from flask import Flask, jsonify, render_template
import psycopg2
import os

app = Flask(__name__)
#Obtiene una conexión a la base de datos
def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5434"),
        user=os.getenv("DB_USER", "admin"),
        password=os.getenv("DB_PASSWORD", "admin"),
        database=os.getenv("DB_NAME", "scrapingdb")
    )
# Endpoint para obtener los resultados de scraping de Tienda Monge
@app.get("/results")
def get_results():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, title, price, url, created_at 
        FROM products
        WHERE url LIKE '%tiendamonge.com%';
    """)
    rows = cursor.fetchall()
    conn.close()
#Convierte los resultados a formato JSON
    products = []
    for r in rows:
        products.append({
            "id": r[0],
            "title": r[1],
            "price": float(r[2]) if r[2] is not None else None,
            "url": r[3],
            "created_at": str(r[4])
        })

    return jsonify(products)

@app.get("/")
def index():
    return render_template("index.html")

app.run(debug=True, port=5000)
