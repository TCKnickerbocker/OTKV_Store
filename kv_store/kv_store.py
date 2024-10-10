# kv_store.py
import threading

# Global key-value store
kv_store = {}
# Threading lock for safe access
kv_lock = threading.Lock()
