import logging
import threading
from queue import Queue
from flask import Flask, request, jsonify
from get_value import get_value
from set_value import set_value
from delete_key import delete_key
from kv_store import kv_store
import time

app = Flask(__name__)

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

# Helper function to handle retries for getting a value
def handle_get_thread(key, timeout=0.01):
    result = [None]
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
    if thread.is_alive():
        return None
    return result[1]

# Helper function to handle retries for deleting a key
def handle_delete_thread(key, timeout=0.01):
    result = [None]
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
    return result[1]

# Set a key-value pair
@app.route('/<key>', methods=['POST'])
def set_value_app(key):
    # Get data
    data = request.get_json()
    if 'value' not in data:
        return jsonify({"error": "Missing 'value' in request body"}), 400
    # Call handler, return appropriately
    res = handle_set_thread(key, data['value'])
    log_operation('set', key, 'success' if res else 'timeout')
    if res is None:
        return jsonify({"error": "Timeout setting value"}), 504
    return jsonify({"message": f"Value for key '{key}' set successfully."}), 200

# Get the value for a key
@app.route('/<key>', methods=['GET'])
def get_value_app(key):
    # Get result, return appropraitely
    res = handle_get_thread(key)
    log_operation('get', key, 'success' if res else 'not found')
    if res is None:
        return jsonify({"error": f"Key '{key}' not found"}), 404
    return jsonify({"value": res}), 200

# Delete a key
@app.route('/<key>', methods=['DELETE'])
def delete_value_app(key):
    # Get result, return appropraitely  
    res = handle_delete_thread(key)
    log_operation('delete', key, 'success' if res else 'timeout')
    if res is None:
        return jsonify({"error": "Timeout deleting key"}), 504
    return jsonify({"message": f"Key '{key}' deleted successfully."}), 200

# Periodic logging of entire kv_store
def print_pulse():
    threading.Timer(10.0, print_pulse).start()
    try:
        with open("../logs/kv_store_contents.log", "w") as logfile:
            logfile.write(f"{time.ctime()}: {kv_store}\n")
    except Exception as e:
        print(f"Error writing to log file: {e}")

if __name__ == '__main__':
    pulse_thread = threading.Thread(target=print_pulse, daemon=True)
    pulse_thread.start()
    app.run(port=8080)

    # Cleanup: Close log worker thread when Flask exits
    log_queue.put(None)
    log_thread.join()
