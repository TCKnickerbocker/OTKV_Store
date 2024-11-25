import threading
import queue
import requests
import time
import xxhash  
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import concurrent.futures

# Configure multiple nodes
BASE_URLS = ['http://127.0.0.1:8080', 'http://127.0.0.1:8081', 'http://127.0.0.1:8082']
# BASE_URLS = ['http://127.0.0.1:8080']

# Configure the number of threads and operations
NUM_THREADS = 10
OPS_PER_THREAD = 100
PRINT_INTERVAL = 1

# Queues for managing latencies
latencies_queue = queue.Queue()

# Synchronize the starting of threads
start_event = threading.Event()

# Session management for connection pooling
def create_session():
    session = requests.Session()
    # Configure connection pooling
    adapter = HTTPAdapter(
        pool_connections=NUM_THREADS,
        pool_maxsize=NUM_THREADS * 2,
        max_retries=Retry(
            total=0,  # No retries for benchmark accuracy
            backoff_factor=0
        )
    )
    session.mount('http://', adapter)
    return session

# Global session pool
sessions = [create_session() for _ in range(NUM_THREADS)]
session_pool = queue.Queue()
for session in sessions:
    session_pool.put(session)

def fast_hash(key, num_nodes):
    return xxhash.xxh64(key.encode()).intdigest() % num_nodes

def kv_store_operation(session, op_type, key, value=None):
    node_index = fast_hash(key, len(BASE_URLS))
    base_url = BASE_URLS[node_index]
    
    try:
        if op_type == 'set':
            response = session.post(
                f"{base_url}/{key}", 
                json={'value': value},
                timeout=1
            )
        elif op_type == 'get':
            response = session.get(
                f"{base_url}/{key}",
                timeout=1
            )
        elif op_type == 'delete':
            response = session.delete(
                f"{base_url}/{key}",
                timeout=1
            )
        else:
            raise ValueError("Invalid operation type")
        
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"Error during {op_type} operation for key '{key}': {e}")
        return False

def batch_worker(batch):
    """Process a batch of operations"""
    session = session_pool.get()
    try:
        results = []
        for op, key, value in batch:
            start_time = time.time()
            if kv_store_operation(session, op, key, value):
                latency = time.time() - start_time
                results.append(latency)
        return results
    finally:
        session_pool.put(session)

def monitor_performance():
    last_print = time.time()
    while True:
        time.sleep(PRINT_INTERVAL)
        current_time = time.time()
        elapsed_time = current_time - last_print
        
        latencies = []
        while not latencies_queue.empty():
            try:
                latencies.append(latencies_queue.get_nowait())
            except queue.Empty:
                break
            
        if latencies:
            avg_latency = sum(latencies) / len(latencies)
            throughput = len(latencies) / elapsed_time
            print(f"[Last {PRINT_INTERVAL} seconds] Throughput: {throughput:.2f} ops/sec, "
                  f"Avg Latency: {avg_latency:.5f} sec/ops")
        
        last_print = current_time

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
    batch_size = 30  # Adjust based on your needs
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
        for future in concurrent.futures.as_completed(futures):
            for latency in future.result():
                latencies_queue.put(latency)

    # Calculate final results
    total_time = time.time() - start_time
    total_ops = NUM_THREADS * OPS_PER_THREAD * 3

    # Collect all latencies
    total_latencies = []
    while not latencies_queue.empty():
        try:
            total_latencies.append(latencies_queue.get_nowait())
        except queue.Empty:
            break

    average_latency = sum(total_latencies) / len(total_latencies) if total_latencies else float('nan')
    throughput = total_ops / total_time

    print("\nFinal Results:")
    print(f"Total operations: {total_ops}")
    print(f"Total time: {total_time:.2f} seconds")
    print(f"Throughput: {throughput:.2f} operations per second")
    print(f"Average Latency: {average_latency:.5f} seconds per operation")

if __name__ == "__main__":
    main()
