use std::collections::HashMap;
use std::env;
use std::sync::{Arc, Mutex};

use hashring::HashRing;
use redis::{Client, Connection, RedisResult, ToRedisArgs, FromRedisValue};

pub struct KvStore {
    store: Arc<Mutex<HashMap<String, String>>>,
    use_redis: bool,
    redis_clients: HashMap<String, Client>,
    ring: HashRing<String>,
}

impl KvStore {
    pub fn new(num_nodes: usize, use_redis: bool, base_port: u16) -> Self {
        let redis_host = env::var("REDIS_HOST").unwrap_or_else(|_| "localhost".to_string());
        let docker_env = env::var("DOCKER_ENV").is_ok();

        let mut nodes = Vec::new();
        let mut node_names = Vec::new();

        if docker_env {
            // Docker environment with named services
            for i in 0..num_nodes {
                nodes.push(format!("redis-{}", i + 1));
                node_names.push(format!("node{}", i + 1));
            }
        } else {
            // Local development with different ports
            for i in 0..num_nodes {
                nodes.push(format!("{}:{}", redis_host, base_port + i as u16));
                node_names.push(format!("node{}", i + 1));
            }
        }

        let ring = HashRing::new(node_names.clone());
        let mut redis_clients = HashMap::new();
        let mut actual_use_redis = use_redis;

        if use_redis {
            for (idx, node) in nodes.iter().enumerate() {
                match Client::open(format!("redis://{}", node)) {
                    Ok(client) => {
                        // Test connection
                        match client.get_connection() {
                            Ok(_) => {
                                println!("Connected to Redis {} as {}", node, node_names[idx]);
                                redis_clients.insert(node_names[idx].clone(), client);
                            }
                            Err(e) => {
                                eprintln!("Redis connection failed for {}: {}", node, e);
                                if idx == 0 {
                                    eprintln!("Primary Redis connection failed. Using in-memory store.");
                                    actual_use_redis = false;
                                    break;
                                }
                            }
                        }
                    }
                    Err(e) => {
                        eprintln!("Failed to create Redis client for {}: {}", node, e);
                        if idx == 0 {
                            actual_use_redis = false;
                            break;
                        }
                    }
                }
            }
        }

        KvStore {
            store: Arc::new(Mutex::new(HashMap::new())),
            use_redis: actual_use_redis,
            redis_clients,
            ring,
        }
    }

    fn get_node(&self, key: &str) -> Option<String> {
        self.ring.get_node(key).cloned()
    }

    pub fn get(&self, key: &str) -> Option<String> {
        if self.use_redis {
            if let Some(node) = self.get_node(key) {
                if let Some(client) = self.redis_clients.get(&node) {
                    match client.get_connection() {
                        Ok(mut conn) => {
                            match conn.get::<_, Option<String>>(key) {
                                Ok(value) => return value,
                                Err(e) => eprintln!("Redis get error: {}", e),
                            }
                        }
                        Err(e) => eprintln!("Redis connection error: {}", e),
                    }
                }
            }
        }

        // Fallback to in-memory store
        self.store.lock().unwrap().get(key).cloned()
    }

    pub fn set(&mut self, key: &str, value: &str) -> RedisResult<()> {
        if self.use_redis {
            if let Some(node) = self.get_node(key) {
                if let Some(client) = self.redis_clients.get(&node) {
                    match client.get_connection() {
                        Ok(mut conn) => {
                            conn.set(key, value)?;
                            println!("Key: {} set successfully in Redis", key);
                            return Ok(());
                        }
                        Err(e) => eprintln!("Redis connection error: {}", e),
                    }
                }
            }
        }

        // Fallback to in-memory store
        self.store.lock().unwrap().insert(key.to_string(), value.to_string());
        Ok(())
    }

    pub fn delete(&mut self, key: &str) -> Vec<i64> {
        let mut results = Vec::new();

        if self.use_redis {
            if let Some(node) = self.get_node(key) {
                if let Some(client) = self.redis_clients.get(&node) {
                    match client.get_connection() {
                        Ok(mut conn) => {
                            match conn.del(key) {
                                Ok(deleted_count) => {
                                    results.push(deleted_count);
                                    return results;
                                }
                                Err(e) => eprintln!("Redis delete error: {}", e),
                            }
                        }
                        Err(e) => eprintln!("Redis connection error: {}", e),
                    }
                }
            }
        }

        // Fallback to in-memory store
        let removed = self.store.lock().unwrap().remove(key).is_some();
        results.push(if removed { 1 } else { 0 });
        results
    }

    pub fn keys(&self, pattern: &str) -> Vec<String> {
        if self.use_redis {
            let mut all_keys = Vec::new();
            for client in self.redis_clients.values() {
                match client.get_connection() {
                    Ok(mut conn) => {
                        match redis::cmd("KEYS").arg(pattern).query(&mut conn) {
                            Ok(keys) => all_keys.extend(keys),
                            Err(e) => eprintln!("Redis keys error: {}", e),
                        }
                    }
                    Err(e) => eprintln!("Redis connection error: {}", e),
                }
            }
            all_keys
        } else {
            self.store
                .lock()
                .unwrap()
                .keys()
                .filter(|k| k.matches(pattern).count() > 0)
                .cloned()
                .collect()
        }
    }
}

// Example usage
fn main() {
    let mut kv_store = KvStore::new(3, true, 6379);
    
    // Set some values
    kv_store.set("key1", "value1").unwrap();
    kv_store.set("key2", "value2").unwrap();

    // Get values
    println!("key1: {:?}", kv_store.get("key1"));
    
    // Delete a key
    kv_store.delete("key1");

    // List keys
    println!("All keys: {:?}", kv_store.keys("*"));
}
