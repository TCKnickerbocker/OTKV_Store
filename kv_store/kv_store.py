# kv_store.py
import threading
import redis
import os

# Retrieve Redis host and port from environment variables, with defaults
redis_host = os.getenv("REDIS_HOST", "localhost")
redis_port = int(os.getenv("REDIS_PORT", 6379))

# Attempt to connect to Redis and use an in-memory store as a backup
class KVStore:
    def __init__(self, use_redis=True):
        self.store = {}  # In-memory dictionary as backup
        self.use_redis = use_redis
        if use_redis:
            try:
                # Attempt to initialize Redis client
                self.redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
                # Test connection by pinging Redis
                self.redis_client.ping()
                print("Connected to Redis")
            except redis.exceptions.ConnectionError:
                print("Redis connection failed. Using in-memory store as backup.")
                self.use_redis = False  # Fallback to in-memory store

    def get(self, key):
        # Retrieve value from Redis if available, otherwise from the in-memory store
        if self.use_redis:
            return self.redis_client.get(key)
        return self.store.get(key)

    def set(self, key, value, **kwargs):
        # Set value in Redis if available, otherwise in the in-memory store
        if self.use_redis:
            self.redis_client.set(key, value, **kwargs)
        else:
            self.store[key] = value
        return 0

    def delete(self, key):
        # Delete key(s) from Redis if available, otherwise from the in-memory store
        res = []  # Could be modified key -> *keys to delete multiple keys at once & return list of responses
        if self.use_redis:
            res.append(self.redis_client.delete(key))
        else:
            res.append(self.store.pop(key, -1))
        return res

    def keys(self, pattern="*"):
        # List keys from Redis if available, otherwise from the in-memory store
        if self.use_redis:
            return self.redis_client.keys(pattern)
        return list(self.store.keys())

kv_store = KVStore(use_redis=True)
kv_lock = threading.Lock()

