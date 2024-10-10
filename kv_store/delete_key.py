# delete_key.py
from kv_store import kv_store, kv_lock

def delete_key(key):
    # Safely delete the key from the kv_store using the lock
    with kv_lock:
        if key in kv_store:
            del kv_store[key]
            return f"Key '{key}' deleted successfully."
        return f"Key '{key}' not found."
