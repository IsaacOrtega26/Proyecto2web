from flask import Flask, jsonify
import psycopg2

app = Flask(__name__)

@app.get("/results")
def get_results():
    conn = psycopg2.connect(host="localhost", user="admin", password="admin", database="scrapingdb")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    data = cursor.fetchall()
    return jsonify(data)

app.run(debug=True, port=5000)