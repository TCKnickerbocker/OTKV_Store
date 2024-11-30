import threading
import queue
from collections import deque
import requests
import time
import xxhash  
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import concurrent.futures
from uhashring import HashRing
import matplotlib.pyplot as plt

# Configure multiple nodes
BASE_URLS = ['http://127.0.0.1:8080', 'http://127.0.0.1:8081', 'http://127.0.0.1:8082']
# BASE_URLS = ['http://127.0.0.1:8080']

# Configure the number of threads and operations
NUM_THREADS = 10
OPS_PER_THREAD = 800
PRINT_INTERVAL = 1

# Queues for managing latencies
latencies_queue = deque()

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
        pool_connections=NUM_THREADS*2,
        pool_maxsize=NUM_THREADS * 4,
        max_retries=Retry(
            total=8
        )
    )
    session.mount('http://', adapter)
    return session

# Global session pool
sessions = [create_session() for _ in range(NUM_THREADS)]
session_pool = queue.Queue()
for session in sessions:
    session_pool.put(session)

# def fast_hash(key, num_nodes):
#     return xxhash.xxh64(key.encode()).intdigest() % num_nodes

def kv_store_operation(session, op_type, key, value=None):
    node = ring.get_node(key)
    base_url = node
    
    try:
        if op_type == 'set':
            response = session.post(
                f"{base_url}/{key}", 
                json={'value': value},
            )
        elif op_type == 'get':
            response = session.get(
                f"{base_url}/{key}",
            )
        elif op_type == 'delete':
            response = session.delete(
                f"{base_url}/{key}",
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
    local_latencies = []  # Use thread-local storage
    error_count = 0
    try:
        for op, key, value in batch:
            start_time = time.time()
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
                pass
            local_latencies.append(time.time() - start_time)
        return local_latencies
    finally:
        session_pool.put(session)

def monitor_performance():
    last_print = time.time()
    while True:
        time.sleep(PRINT_INTERVAL)
        current_time = time.time()
        elapsed_time = current_time - last_print
        
        latencies = []
        while latencies_queue:
            try:
                latencies.append(latencies_queue.popleft())
            except IndexError:
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
    batch_size = 375  # Adjust based on your needs
    batches = [operations[i:i + batch_size] for i in range(0, len(operations), batch_size)]

    # Start the monitoring thread
    monitoring_thread = threading.Thread(target=monitor_performance, daemon=True)
    monitoring_thread.start()

    # Starting benchmark
    start_time = time.time()

    # Collect all latencies for plotting
    all_latencies = []

    # Use ThreadPoolExecutor for better thread management
    with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
        # Submit all batches and collect futures
        futures = [executor.submit(batch_worker, batch) for batch in batches]
        
        # Collect results as they complete
        for future in concurrent.futures.as_completed(futures):
            batch_latencies = future.result()
            for latency in batch_latencies:
                latencies_queue.append(latency)
                all_latencies.append(latency)

    # Calculate final results
    total_time = time.time() - start_time
    total_ops = NUM_THREADS * OPS_PER_THREAD * 3

    # Collect all latencies
    total_latencies = []
    while latencies_queue:
        try:
            total_latencies.append(latencies_queue.popleft())
        except IndexError:
            break

    average_latency = sum(total_latencies) / len(total_latencies) if total_latencies else float('nan')
    throughput = total_ops / total_time
    error_rate = error_count / total_ops

    print("\nFinal Results:")
    print(f"Total operations: {total_ops}")
    print(f"Total time: {total_time:.2f} seconds")
    print(f"Throughput: {throughput:.2f} operations per second")
    print(f"Average Latency: {average_latency:.5f} seconds per operation")
    print(f"Error Rate: {error_rate:.4f}%")

    kv1 = 0
    kv2 = 0
    kv3 = 0
    num_nodes = len(kv_stores)
    
    for node in kv_stores:
        if node == 'http://127.0.0.1:8080':
            kv1 += 1
        elif node == 'http://127.0.0.1:8081':
            kv2 += 1
        else:
            kv3 += 1
    print(f"Percent of 8080 calls: {kv1/len(num_nodes) * 100:.4f}%")
    print(f"Percent of 8081 calls: {kv2/len(num_nodes) * 100:.4f}%")
    print(f"Percent of 8082 calls: {kv3/len(num_nodes) * 100:.4f}%")
    
    
    # Plotting Latency
    plural = "" if len(num_nodes) == 1 else "s"
    plt.figure(figsize=(12, 6))
    plt.plot(range(len(all_latencies)), all_latencies, marker='.', linestyle='', alpha=0.5)
    plt.title(f'Latency per Operation ({len(num_nodes)} node{plural}, with monitoring code)')
    plt.xlabel('Operation Number')
    plt.ylabel('Latency (seconds)')
    plt.tight_layout()
    plt.savefig('latency_plot.png')
    plt.close()

if __name__ == "__main__":
    main()