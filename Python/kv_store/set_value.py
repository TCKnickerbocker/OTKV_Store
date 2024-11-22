# set_value.py
from kv_store import kv_store
from lock_manager import kv_lock
import threading

# Helper function to handle retries for setting a key-value pair
def handle_set_thread(key, value, timeout=0.01):
    result = [None]
    # Call thread, append results to result
    thread = threading.Thread(target=lambda: result.append(set_value(key, value)))
    thread.start()
    thread.join(timeout)

    # If timeout occurs, send another thread out
    if thread.is_alive():
        thread = threading.Thread(target=lambda: result.append(set_value(key, value)))
        thread.start()
        thread.join(timeout)
    # Both threads failed - return failure
    if thread.is_alive():
        return None
    return result[1]

def set_value(key, value):
    # Safely set key-value pair using lock
    with kv_lock:
        kv_store.set(key, value)
        # TODO: Forward to next in chain
        return 0
