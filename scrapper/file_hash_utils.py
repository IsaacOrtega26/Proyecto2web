import hashlib

def get_file_hash(path):
    try:
        with open(path, "rb") as f:
            file_bytes = f.read()
            hash_value = hashlib.md5(file_bytes).hexdigest()
            return hash_value
    except:
        return None
