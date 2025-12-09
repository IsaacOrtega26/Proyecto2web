# api/json_api_server.py

import os
import sys
from flask import Flask, jsonify, render_template

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from scrapper.db_utils import get_connection  # ahora sí lo encuentra


app = Flask(__name__, template_folder="templates")


@app.get("/results")
def get_results():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, title, price, url, created_at
        FROM products
        ORDER BY created_at DESC;
    """)
    rows = cur.fetchall()

    cur.close()
    conn.close()

    products = []
    for r in rows:
        products.append({
            "id": r[0],
            "title": r[1],
            "price": float(r[2]) if r[2] is not None else None,
            "url": r[3],
            "created_at": r[4].isoformat() if hasattr(r[4], "isoformat") else str(r[4]),
        })

    return jsonify(products)


@app.get("/")
def index():
    """
    Renderiza el dashboard (tabla con filtros).
    """
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
