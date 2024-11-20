import threading
import argparse
import sys
import uvicorn
sys.path.append("./kv_store")

from logger import log_queue, log_thread, log_entire_store
from endpoint import api


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Start KV Store server')
    parser.add_argument('--nodes', type=int, default=3, help='Number of Redis nodes to create (default: 3)')
    parser.add_argument('--base-port', type=int, default=6380, help='Base port number for Redis nodes (default: 6379)')
    parser.add_argument('--port', type=int, default=8080, help='Port to run the FastAPI application (default: 8080)')
    args = parser.parse_args()
    
    pulse_thread = threading.Thread(target=log_entire_store, daemon=True)
    pulse_thread.start()
    
    try:  # Run API
        uvicorn.run(
            "main:api",
            host='0.0.0.0', 
            port=args.port,
            reload=True 
        )
    except KeyboardInterrupt:
        pass
    finally:  # Cleanup
        log_queue.put(None)
        log_thread.join()
    