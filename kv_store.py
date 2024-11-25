# kv_store.py
import threading
import redis
import os
from uhashring import HashRing


class KVStore:
    def __init__(self, num_nodes=3, use_redis=False, user_serverside_hashring=False, base_port=6379):
        """
        Initialize KV Store with dynamic number of nodes
        
        Args:
            num_nodes (int): Number of Redis nodes to create
            use_redis (bool): Whether to use Redis or fallback to in-memory
            base_port (int): Starting port number for Redis nodes
        """
        self.store = {}  # In-memory dictionary as backup
        self.use_redis = use_redis
        self.redis_clients = {}
        
        # Generate nodes configuration
        self.nodes = []
        redis_host = os.getenv("REDIS_HOST", "localhost")
        
        # In Docker, we need to handle multiple Redis services
        if os.getenv("DOCKER_ENV"):
            # Expect Redis services to be named redis-1, redis-2, etc.
            for i in range(num_nodes):
                self.nodes.append({
                    "host": f"redis-{i+1}",  # Docker service name
                    "port": base_port  # Each service runs on the same port
                })
        else:
            # Local development - use different ports on localhost
            for i in range(num_nodes):
                self.nodes.append({
                    "host": redis_host,
                    "port": base_port + i
                })

        # Initialize HashRing with node names
        node_names = [f"node{i+1}" for i in range(num_nodes)]
        self.ring = HashRing(nodes=node_names)

        if use_redis:
            for idx, node in enumerate(self.nodes):
                try:
                    # Attempt to initialize Redis client
                    client = redis.Redis(
                        host=node['host'], 
                        port=node['port'], 
                        decode_responses=True,
                        socket_connect_timeout=2.0  # Add timeout for connection attempts
                    )
                    # Test connection by pinging Redis
                    client.ping()
                    self.redis_clients[f"node{idx+1}"] = client
                    print(f"Connected to Redis {node['host']}:{node['port']} as node{idx+1}")
                except (redis.exceptions.ConnectionError, redis.exceptions.TimeoutError) as e:
                    print(f"Redis connection failed for {node['host']}:{node['port']}: {str(e)}")
                    if idx == 0:  # If first node fails, fallback to in-memory
                        print("Primary Redis connection failed. Using in-memory store as backup.")
                        self.use_redis = False
                        break

    def get_client(self, key):
        node = self.ring.get_node(key)
        return self.redis_clients.get(node)

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
            print("Failed to get client or use_redis == False")
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

kv_store = KVStore(num_nodes=1)
