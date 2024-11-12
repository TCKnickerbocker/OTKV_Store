import threading
import argparse
import sys
sys.path.append("./kv_store")

from logger import log_queue, log_thread, log_entire_store
from app import app


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Start KV Store server')
    parser.add_argument('--nodes', type=int, default=3, help='Number of Redis nodes to create (default: 3)')
    parser.add_argument('--base-port', type=int, default=6379, help='Base port number for Redis nodes (default: 6379)')
    parser.add_argument('--port', type=int, default=8080, help='Port to run the Flask application (default: 8080)')
    args = parser.parse_args()
    
    # kv_store = kv_store.KVStore(num_nodes=args.nodes, base_port=args.base_port)
    
    pulse_thread = threading.Thread(target=log_entire_store, daemon=True)
    pulse_thread.start()
    app.run(host='0.0.0.0', port=args.port)

    # Cleanup: Close log worker thread when Flask exits
    log_queue.put(None)
    log_thread.join()
