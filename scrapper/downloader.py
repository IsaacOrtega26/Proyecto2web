# scrapper/downloader.py

import os
import hashlib
import requests
from scrapper.db_utils import log_change, get_connection, FILES_DIR

# Usamos la misma carpeta de db_utils (FILES_DIR)
FILES_PATH = FILES_DIR  # normalmente /data/files dentro del contenedor


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
    """Descarga un archivo desde URL al filesystem y devuelve la ruta local."""
    try:
        resp = requests.get(url, timeout=10)
    except Exception as e:
        print("Error de red descargando archivo:", url, e)
        log_change(f"ERROR descargando archivo {url}: {e}")
        return None

    if resp.status_code != 200:
        print("Error descargando archivo:", url, "status:", resp.status_code)
        log_change(f"ERROR descargando archivo {url}: status {resp.status_code}")
        return None

    file_path = os.path.join(FILES_PATH, filename)  

    with open(file_path, "wb") as f:
        f.write(resp.content)

    return file_path



def process_files():
    """
    Lee productos desde BD y descarga los archivos.
    Revisa cambios en hash y actualiza file_control.
    """
    ensure_folder()

    conn = get_connection()
    cur = conn.cursor()

    # Aquí asumes que en products.url está el link al archivo (pdf/imagen/etc).
    cur.execute("""
        SELECT id, url
        FROM products
        WHERE url IS NOT NULL AND url != ''
    """)
    products = cur.fetchall()

    for product_id, url in products:
        if not url:
            continue

        filename = f"{product_id}.bin"  # puede ser imagen, pdf, etc
        file_path = os.path.join(FILES_PATH, filename)

        # Descargar archivo temporal para calcular hash nuevo
        tmp_path = download_file(url, filename + ".tmp")
        if not tmp_path:
            continue

        new_hash = hash_file(tmp_path)

        # Consultar hash anterior en file_control
        cur.execute("SELECT hash FROM file_control WHERE product_id=%s", (product_id,))
        prev = cur.fetchone()

        # no existía registro ingresa NUEVO ARCHIVO
        if not prev:
            os.rename(tmp_path, file_path)
            cur.execute(
                "INSERT INTO file_control(product_id, filename, hash) VALUES (%s, %s, %s)",
                (product_id, filename, new_hash),
            )
            conn.commit()

            log_change(f"NUEVO ARCHIVO — Producto {product_id} → {filename}")
            print("Nuevo archivo guardado →", filename)
            continue

        prev_hash = prev[0]

        # contenido cambió a "ARCHIVO MODIFICADO"
        if prev_hash != new_hash:
            # borrar archivo viejo si existe
            if os.path.exists(file_path):
                os.remove(file_path)

            os.rename(tmp_path, file_path)

            cur.execute(
                "UPDATE file_control SET hash=%s, updated_at=NOW() WHERE product_id=%s",
                (new_hash, product_id),
            )
            conn.commit()

            log_change(f"ARCHIVO MODIFICADO — Producto {product_id} → {filename}")
            print("Archivo actualizado →", filename)

        else:
            # mismo hash → no hay cambios, borrar temporal
            os.remove(tmp_path)
            print(f"Archivo sin cambios para producto {product_id}")

    cur.close()
    conn.close()


if __name__ == "__main__":
    print("Procesando archivos…")
    process_files()
    print("✔ Descarga finalizada ✔")
