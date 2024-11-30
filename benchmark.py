import threading
import queue
import requests
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import concurrent.futures
from uhashring import HashRing

# Configure multiple nodes
BASE_URLS = ['http://127.0.0.1:8080', 'http://127.0.0.1:8081', 'http://127.0.0.1:8082']

# Configure the number of threads and operations
NUM_THREADS = 10
OPS_PER_THREAD = 800
PRINT_INTERVAL = 1

error_count = 0
kv_stores = []
ring = HashRing(BASE_URLS, hash_fn='ketama')

# Synchronize the starting of threads
start_event = threading.Event()

# Session management for connection pooling
def create_session():
    session = requests.Session()
    # Configure connection pooling
    adapter = HTTPAdapter(
        pool_connections=NUM_THREADS * 2,
        pool_maxsize=NUM_THREADS * 4,
        max_retries=Retry(total=8)
    )
    session.mount('http://', adapter)
    return session

# Global session pool
sessions = [create_session() for _ in range(NUM_THREADS)]
session_pool = queue.Queue()
for session in sessions:
    session_pool.put(session)

def batch_worker(batch):
    """Process a batch of operations"""
    session = session_pool.get()
    error_count = 0
    try:
        for op, key, value in batch:
            node = ring.get_node(key)
            base_url = node
            kv_stores.append(node)
            try:
                if op == 'set':
                    session.post(f"{base_url}/{key}", json={'value': value}).raise_for_status()
                elif op == 'get':
                    session.get(f"{base_url}/{key}").raise_for_status()
            except Exception:
                error_count += 1
        return error_count
    finally:
        session_pool.put(session)

def monitor_performance():
    while True:
        time.sleep(PRINT_INTERVAL)

def main():
    # Create all operations upfront
    operations = []
    for i in range(NUM_THREADS * OPS_PER_THREAD):
        operations.extend([
            ('set', f"key_{i}", f"value_{i}"),
            ('get', f"key_{i}", None),
            ('delete', f"key_{i}", None)
        ])

    # Split operations into batches for better efficiency
    batch_size = 375  # Adjust based on your needs
    batches = [operations[i:i + batch_size] for i in range(0, len(operations), batch_size)]

    # Start the monitoring thread
    monitoring_thread = threading.Thread(target=monitor_performance, daemon=True)
    monitoring_thread.start()

    # Starting benchmark
    start_time = time.time()

    # Use ThreadPoolExecutor for better thread management
    with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
        # Submit all batches and collect futures
        futures = [executor.submit(batch_worker, batch) for batch in batches]
        
        # Collect results as they complete
        total_errors = sum(future.result() for future in concurrent.futures.as_completed(futures))

    # Calculate final results
    total_time = time.time() - start_time
    total_ops = NUM_THREADS * OPS_PER_THREAD * 3
    
    average_latency = total_time / total_ops
    throughput = total_ops / total_time
    error_rate = total_errors / total_ops

    print("\nFinal Results:")
    print(f"Total operations: {total_ops}")
    print(f"Total time: {total_time:.2f} seconds")
    print(f"Throughput: {throughput:.2f} operations per second")
    print(f"Average Latency: {average_latency:.5f} seconds per operation")
    print(f"Error Rate: {error_rate:.4f}%")

if __name__ == "__main__":
    main()
