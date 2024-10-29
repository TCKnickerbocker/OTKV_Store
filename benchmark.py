'''
Benchmark for testing kv store
Every other request is a get for a key that hasn't been instantiated... 
odd = get, even = set
'''

import threading
import queue
import requests
import time
import random

# The base URL of the Flask server
BASE_URL = 'http://127.0.0.1:8080'

# Configure the number of threads and operations
NUM_THREADS = 3
OPS_PER_THREAD = 100
# OPS_PER_THREAD = 2

PRINT_INTERVAL = 3  # Interval for printing intermediate results

# Queues for managing operations and latencies
operations_queue = queue.Queue()
latencies_queue = queue.Queue()

# Synchronize the starting of threads
start_event = threading.Event()

# Client operation function
def kv_store_operation(op_type, key, value=None):
    try:
        if op_type == 'set':
            response = requests.post(f"{BASE_URL}/{key}", json={'value': value})
        elif op_type == 'get':
            response = requests.get(f"{BASE_URL}/{key}")
        elif op_type == 'delete':
            response = requests.delete(f"{BASE_URL}/{key}")
        else:
            raise ValueError("Invalid operation type")
        response.raise_for_status()  # This will raise an error for non-2xx responses
        return True
    except Exception as e:
        print(f"Error during {op_type} operation for key '{key}': {e}")
        return False

# Worker thread function
def worker_thread():
    while not start_event.is_set():
        # Wait until all threads are ready to start
        pass

    while not operations_queue.empty():
        op, key, value = operations_queue.get()
        start_time = time.time()
        if kv_store_operation(op, key, value):
            latency = time.time() - start_time
            latencies_queue.put(latency)

# Monitoring thread function
def monitor_performance():
    last_print = time.time()
    while True:
        time.sleep(PRINT_INTERVAL)
        current_time = time.time()
        elapsed_time = current_time - last_print
        latencies = []
        while not latencies_queue.empty():
            latencies.append(latencies_queue.get())

        if latencies:
            avg_latency = sum(latencies) / len(latencies)
            throughput = len(latencies) / elapsed_time
            print(f"[Last {PRINT_INTERVAL} seconds] Throughput: {throughput:.2f} ops/sec, "
                  f"Avg Latency: {avg_latency:.5f} sec/ops")
        last_print = time.time()

'''
# Populate the operation queue with mixed 'set' and 'get' requests
for i in range(NUM_THREADS * OPS_PER_THREAD):
    op_type = 'get' if i % 2 else 'set'
    key = f"key_{i}"
    value = f"value_{i}" if op_type == 'set' else None
    operations_queue.put((op_type, key, value))
'''



# A set to keep track of keys that are successfully set
existing_keys = set()

# Populate the operation queue with mixed 'set', 'get', and 'delete' requests
keys = ['a', 'b', 'c', 'd', 'e']

for i in range(NUM_THREADS * OPS_PER_THREAD):
    op_type = random.choice(['get', 'set', 'delete'])
    key = random.choice(keys)
    value = f"value_{i}" if op_type == 'set' else None
    print(op_type, key, value)
    operations_queue.put((op_type, key, value))



# Create and start worker threads
threads = [threading.Thread(target=worker_thread) for _ in range(NUM_THREADS)]

# Start the monitoring thread
monitoring_thread = threading.Thread(target=monitor_performance, daemon=True)
monitoring_thread.start()

# Starting benchmark
start_time = time.time()
start_event.set()  # Signal threads to start

for thread in threads:
    thread.start()

for thread in threads:
    thread.join()

# Calculate final results
total_time = time.time() - start_time
total_ops = NUM_THREADS * OPS_PER_THREAD * 2  # times two for 'set' and 'get'
total_latencies = list(latencies_queue.queue)
average_latency = sum(total_latencies) / len(total_latencies) if total_latencies else float('nan')
throughput = total_ops / total_time

print("\nFinal Results:")
print(f"Total operations: {total_ops}")
print(f"Total time: {total_time:.2f} seconds")
print(f"Throughput: {throughput:.2f} operations per second")
print(f"Average Latency: {average_latency:.5f} seconds per operation")