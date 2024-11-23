# delete_key.py
# from kv_store import kv_store
from trie_kv_store import kv_store
from lock_manager import kv_lock
import threading

# Helper function to handle retries for deleting a key
def handle_delete_thread(key, timeout=0.01):
    result = []
    # Call thread, append results to result
    thread = threading.Thread(target=lambda: result.append(delete_key(key)))
    thread.start()
    thread.join(timeout)
    
    # If timeout occurs, send another thread out
    if thread.is_alive():
        thread = threading.Thread(target=lambda: result.append(delete_key(key)))
        thread.start()
        thread.join(timeout)
        
    # Both threads failed - return failure
    if thread.is_alive():
        return None
    return result


def delete_key(key):
    # Safely delete the key from kv_store using lock
    with kv_lock:
        res = kv_store.delete(key)
        if res is not None:
            return 0  # Key successfully deleted
        return -1  # Key not found
