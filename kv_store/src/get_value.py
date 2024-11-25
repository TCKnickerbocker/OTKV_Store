# get_value.py
# from kv_store import kv_store
from trie_kv_store import kv_store
import threading

# Helper function to handle retries for getting a value
def handle_get_thread(key, timeout=0.01):
    result = [-1]
    # Call thread, append results to result
    thread = threading.Thread(target=lambda: result.append(get_value(key)))
    thread.start()
    thread.join(timeout)

    # If timeout occurs, send another thread out
    if thread.is_alive():
        thread = threading.Thread(target=lambda: result.append(get_value(key)))
        thread.start()
        thread.join(timeout)
        
    # Both threads failed - return failure
    if thread.is_alive() or result[1] == None:
        return "-1"
    return result[1]



def get_value(key):
    # Retrieve value from kv_store
    x = kv_store.get(key)
    return x
