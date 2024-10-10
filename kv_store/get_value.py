# get_value.py
from kv_store import kv_store

def get_value(key):
    # Retrieve value from kv_store
    return kv_store.get(key, None)