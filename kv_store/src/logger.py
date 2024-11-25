import logging
import threading
import time
from queue import Queue
from kv_store import kv_store

# Set up a logging queue
log_queue = Queue()

# Configure logger to use the queue handler
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("kv_store_operations")

# Log worker continuously writes from queue to logfile
def log_worker():
    with open("../logs/kv_store_operations.log", "a") as logfile:
        while True:
            log_entry = log_queue.get()
            if log_entry is None:
                break  # Exit signal received
            logfile.write(log_entry + "\n")
            logfile.flush()  # Ensure log is written to file immediately
    print("Log worker exiting")

# Start the log worker thread
log_thread = threading.Thread(target=log_worker, daemon=True)
log_thread.start()

# Get time & format log operation
def log_operation(operation_type, key, result):
    timestamp = time.ctime()
    log_entry = f"{timestamp} - {operation_type.upper()} - key: {key}, result: {result}"
    log_queue.put(log_entry)


# Periodic logging of entire kv_store
def log_entire_store():
    threading.Timer(10.0, log_entire_store).start()
    try:
        with open("./logs/kv_store_contents.log", "w") as logfile:
            logfile.write(f"{time.ctime()}: {kv_store.get('*')}\n")
    except Exception as e:
        print(f"Error writing to log file: {e}")
        
