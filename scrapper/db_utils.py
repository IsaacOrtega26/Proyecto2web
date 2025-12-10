import os
import psycopg2
from datetime import datetime

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "logs")
LOG_DIR = os.path.normpath(LOG_DIR)
LOG_FILE = os.path.join(LOG_DIR, "changes.log")
FILES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "data", "files")
FILES_DIR = os.path.normpath(FILES_DIR)

# --- Utilidades de entorno / paths ---
def ensure_dirs():
    os.makedirs(LOG_DIR, exist_ok=True)
    os.makedirs(FILES_DIR, exist_ok=True)

def log_change(message: str):
    """Escribe una línea en el log con timestamp y también la imprime."""
    ensure_dirs()
    ts = datetime.now().isoformat()
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{ts} - {message}\n")
    print(f"{ts} - {message}")

# --- Conexión a la BD ---
def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5434"),
        user=os.getenv("DB_USER", "admin"),
        password=os.getenv("DB_PASSWORD", "admin"),
        database=os.getenv("DB_NAME", "scrapingdb"),
    )

# --- Operaciones sobre products ---
def save_products(products):
    """
    Guarda una lista de productos. Cada producto es un dict con keys:
    title, price, url
    """
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
        log_change(f"Guardados {len(products)} productos en la BD.")
    except Exception as e:
        conn.rollback()
        log_change(f"ERROR guardando productos: {e}")
        print("Error guardando productos:", e)
    finally:
        cur.close()
        conn.close()

def get_all_products():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, title, price, url, created_at FROM products ORDER BY id;")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def find_product_by_id(product_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, title, price, url, created_at FROM products WHERE id=%s;", (product_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row

def find_product_by_title(title):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, title, price, url, created_at FROM products WHERE title ILIKE %s LIMIT 1;", (f"%{title}%",))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row

def update_product(product_id, new_price):
    """
    Actualiza el precio de un producto y escribe log.
    """
    conn = get_connection()
    cur = conn.cursor()
    try:
        # optional: obtener precio viejo para log
        cur.execute("SELECT price, title FROM products WHERE id=%s;", (product_id,))
        old = cur.fetchone()
        old_price = old[0] if old else None
        title = old[1] if old else f"id:{product_id}"

        cur.execute("""
            UPDATE products SET price=%s WHERE id=%s
        """, (new_price, product_id))
        conn.commit()

        log_change(f"PRODUCTO ACTUALIZADO - ID {product_id}, '{title}', precio {old_price} → {new_price}")
    except Exception as e:
        conn.rollback()
        log_change(f"ERROR al actualizar producto {product_id}: {e}")
        raise
    finally:
        cur.close()
        conn.close()

def delete_product(product_id):
    """
    Elimina producto de la tabla products y sus archivos asociados (si los hay).
    """
    # eliminar archivos asociados primero
    delete_product_files(product_id)

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT title FROM products WHERE id=%s;", (product_id,))
        row = cur.fetchone()
        title = row[0] if row else f"id:{product_id}"

        cur.execute("DELETE FROM products WHERE id=%s;", (product_id,))
        conn.commit()
        log_change(f"PRODUCTO ELIMINADO - ID {product_id}, '{title}'")
    except Exception as e:
        conn.rollback()
        log_change(f"ERROR al eliminar producto {product_id}: {e}")
        raise
    finally:
        cur.close()
        conn.close()

# --- Operaciones para control de archivos ---
def get_file_record(product_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, product_id, filename, hash, updated_at FROM file_control WHERE product_id=%s;", (product_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row

def save_or_update_file_record(product_id, filename, file_hash):
    """
    Inserta o actualiza el registro en file_control y loggea cambio.
    """
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT hash FROM file_control WHERE product_id=%s;", (product_id,))
        res = cur.fetchone()
        if res is None:
            cur.execute(
                "INSERT INTO file_control (product_id, filename, hash) VALUES (%s, %s, %s);",
                (product_id, filename, file_hash)
            )
            conn.commit()
            log_change(f"FILE_CONTROL: nuevo archivo para product_id={product_id} -> {filename}")
        else:
            old_hash = res[0]
            if old_hash != file_hash:
                cur.execute(
                    "UPDATE file_control SET filename=%s, hash=%s, updated_at=NOW() WHERE product_id=%s;",
                    (filename, file_hash, product_id)
                )
                conn.commit()
                log_change(f"FILE_CONTROL: archivo modificado product_id={product_id} -> {filename} (hash cambiado)")
            else:
                # no hay cambio
                pass
    except Exception as e:
        conn.rollback()
        log_change(f"ERROR file_control product_id={product_id}: {e}")
        raise
    finally:
        cur.close()
        conn.close()

def delete_product_files(product_id):
    """
    Borra el fichero local (si existe) y su registro en file_control.
    """
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT filename FROM file_control WHERE product_id=%s;", (product_id,))
        res = cur.fetchone()
        if res:
            filename = res[0]
            path = os.path.join(FILES_DIR, filename)
            if os.path.exists(path):
                os.remove(path)
                log_change(f"Archivo local eliminado: {path}")
            cur.execute("DELETE FROM file_control WHERE product_id=%s;", (product_id,))
            conn.commit()
            log_change(f"Registro file_control eliminado para product_id={product_id}")
    except Exception as e:
        conn.rollback()
        log_change(f"ERROR al eliminar archivos de product_id={product_id}: {e}")
        raise
    finally:
        cur.close()
        conn.close()