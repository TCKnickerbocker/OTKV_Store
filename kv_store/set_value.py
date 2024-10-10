# set_value.py
from kv_store import kv_store, kv_lock

def set_value(key, value):
    # Safely set key-value pair using lock
    with kv_lock:
        kv_store[key] = value
        return 0
