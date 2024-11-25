import threading
import argparse
import sys
import fastwsgi
import uvicorn
sys.path.append("./kv_store")
from logger import log_entire_store
from app import app

def parse_args():
    parser = argparse.ArgumentParser(description='Start KV Store server')
    parser.add_argument('--nodes', type=int, default=3, help='Number of Redis nodes to create (default: 3)')
    parser.add_argument('--base-port', type=int, default=6379, help='Base port number for Redis nodes (default: 6379)')
    parser.add_argument('--port', type=int, default=8080, help='Port to run the FastAPI application (default: 8080)')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()

    # Start background thread for logging the entire store
    pulse_thread = threading.Thread(target=log_entire_store, daemon=True)
    pulse_thread.start()

    fastwsgi.run(wsgi_app=app, host='0.0.0.0', port=args.port)

