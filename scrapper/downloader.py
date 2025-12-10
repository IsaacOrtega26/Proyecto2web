import os
import hashlib
import requests
from datetime import datetime
from scrapper.db_utils import log_change, get_connection

FILES_PATH = "data/files/"


def ensure_folder():
    """Crea carpeta donde se guardarán los archivos descargados."""
    if not os.path.exists(FILES_PATH):
        os.makedirs(FILES_PATH)


def hash_file(path):
    """Genera hash SHA256 de un archivo local."""
    sha = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(4096), b""):
            sha.update(block)
    return sha.hexdigest()


def download_file(url, filename):
    """Descarga un archivo desde URL al filesystem."""
    response = requests.get(url, timeout=10)

    if response.status_code != 200:
        print("❌ Error descargando archivo:", url)
        return None

    file_path = os.path.join(FILES_PATH, filename)

    with open(file_path, "wb") as f:
        f.write(response.content)

    return file_path


def process_files():
    """
    Lee productos desde BD y descarga los archivos.
    Revisa cambios en hash y elimina antiguos.
    """
    ensure_folder()

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, url
        FROM products
        WHERE url IS NOT NULL AND url != ''
    """)
    products = cur.fetchall()

    for product_id, url in products:
        filename = f"{product_id}.bin"  # puede ser la imagen, pdf, etc
        file_path = os.path.join(FILES_PATH, filename)

        # descargar archivo temporal para validar hash
        tmp_path = download_file(url, filename + ".tmp")
        if not tmp_path:
            continue

        new_hash = hash_file(tmp_path)

        # consultar hash anterior
        cur.execute("SELECT filehash FROM file_control WHERE product_id=%s", (product_id,))
        prev_hash = cur.fetchone()

        # si no existía antes → es nuevo archivo
        if not prev_hash:
            os.rename(tmp_path, file_path)
            cur.execute(
                "INSERT INTO file_control(product_id, filename, filehash) VALUES (%s, %s, %s)",
                (product_id, filename, new_hash))
            conn.commit()

            log_change(f"NUEVO ARCHIVO — Producto {product_id}")
            print("Nuevo archivo guardado →", filename)
            continue

        prev_hash = prev_hash[0]

        # si cambió el contenido
        if prev_hash != new_hash:
            os.remove(file_path)
            os.rename(tmp_path, file_path)

            cur.execute(
                "UPDATE file_control SET filehash=%s WHERE product_id=%s",
                (new_hash, product_id))
            conn.commit()

            log_change(f"ARCHIVO MODIFICADO — Producto {product_id}")
            print("Archivo actualizado →", filename)

        else:
            # si es igual, borrar temporal
            os.remove(tmp_path)

    cur.close()
    conn.close()


if __name__ == "__main__":
    print("Procesando archivos…")
    process_files()
    print("✔ Descarga finalizada ✔")
