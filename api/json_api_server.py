from flask import Flask, jsonify
import psycopg2

app = Flask(__name__)

def get_connection():
    return psycopg2.connect(
        host="localhost",
        port=5434,
        user="admin",
        password="admin",
        database="scrapingdb"
    )

@app.get("/results")
def get_results():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, price, url, created_at FROM products;")
    rows = cursor.fetchall()
    conn.close()

    products = []
    for r in rows:
        products.append({
            "id": r[0],
            "title": r[1],
            "price": float(r[2]) if r[2] else None,
            "url": r[3],
            "created_at": str(r[4])
        })

    return jsonify(products)

app.run(debug=True, port=5000)
