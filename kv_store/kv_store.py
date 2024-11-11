# kv_store.py
import threading
import redis
import os
from uhashring import HashRing

# Setting up nodes for uhashring
nodes = [
    {"host": os.getenv("REDIS_HOST", "localhost"), "port": int(os.getenv("REDIS_PORT", 6379))},
    {"host": os.getenv("REDIS_HOST", "localhost"), "port": int(os.getenv("REDIS_PORT", 6380))},
    {"host": os.getenv("REDIS_HOST", "localhost"), "port": int(os.getenv("REDIS_PORT", 6381))},
]

# Attempt to connect to Redis and use an in-memory store as a backup
class KVStore:
    def __init__(self, use_redis=True):
        self.store = {}  # In-memory dictionary as backup
        self.use_redis = use_redis
        self.ring = HashRing(nodes=['node1'])
        self.redis_clients = {}
        if use_redis:
            for idx, node in enumerate(nodes):
                try:
                    # Attempt to initialize Redis client
                    client = redis.Redis(host=node['host'], port=node['port'], decode_responses=True)
                    # Test connection by pinging Redis
                    client.ping()
                    self.redis_clients[f"node{idx+1}"] = client
                    print(f"Connected to Redis node{idx+1}")
                except redis.exceptions.ConnectionError:
                    print("Redis connection failed. Using in-memory store as backup.")
                    self.use_redis = False  # Fallback to in-memory store

    def get_client(self, key):
        node = self.ring.get_node(key)
        # print(f"Key: {key}, Assigned Node: {node}")
        return self.redis_clients[node]

    def get(self, key):
        # Retrieve value from Redis if available, otherwise from the in-memory store
        client = self.get_client(key)

        if self.use_redis and client:
            return client.get(key)
        return self.store.get(key)

    def set(self, key, value, **kwargs):
        # Set value in Redis if available, otherwise in the in-memory store
        client = self.get_client(key)

        if self.use_redis and client:
            res = client.set(key, value, **kwargs)

            if res == None:
                print(f"Failed to set key: {key} in Redis")
            else:
                print(f"Key: {key} set successfully in Redis")
        else:
            self.store[key] = value
        return 0

    def delete(self, key):
        # Delete key(s) from Redis if available, otherwise from the in-memory store
        res = []  # Could be modified key -> *keys to delete multiple keys at once & return list of responses
        client = self.get_client(key)

        if self.use_redis and client:
            res.append(client.delete(key))
        else:
            res.append(self.store.pop(key, -1))
        return res

    def keys(self, pattern="*"):
        # List keys from Redis if available, otherwise from the in-memory store
        if self.use_redis:
            all_keys = []
            for client in self.redis_clients.values():
                all_keys.extend(client.keys(pattern))
            return all_keys
        return list(self.store.keys())

kv_store = KVStore(use_redis=True)