use hashring::HashRing;
use std::collections::HashMap;
use redis::{Client, Commands, Connection, ConnectionLike, RedisError};
use std::env;
use std::time::Duration;
use std::error::Error;

pub struct KVStore {
    store: HashMap<String, String>,
    use_redis: bool,
    redis_clients: HashMap<String, Connection>,
    nodes: Vec<HashMap<String, u16>>,
    ring: HashRing<String>,
}

// What we return in get()
// TODO: Could have issues with InMemoryStore type
enum ClientKind {
    RedisClient(Client),
    InMemoryStore(String)
}

impl KVStore {
    fn new(num_nodes: u8, use_redis: bool, base_port: u16) -> Self {
        let mut store = HashMap::new();
        let mut redis_clients = HashMap::new();
        let mut nodes = Vec::new();

        let mut redis_host = env::var("REDIS_HOST").unwrap_or("localhost".to_string());

        match env::var("DOCKER_ENV") {
            Ok(docker) => {
                for i in 0..num_nodes {
                    let mut node: HashMap<String, u16> = HashMap::new();
                    node.insert(format!("redis-{}", i+1), base_port);
                    nodes.push(node);
                }
            }
            Err(e) => {
                for i in 0..num_nodes {
                    let mut node: HashMap<String, u16> = HashMap::new();
                    node.insert(redis_host, base_port+i);
                    nodes.push(node);
                }
            }
        }

        let mut node_names: Vec<String> = Vec::new();

        for i in 0..num_nodes {
            node_names.push(format!("node{}", i+1))
        }

        let mut ring = HashRing::new();

        for name in node_names {
            ring.add(name);
        }

        if use_redis {
            for (idx, node) in nodes.iter().enumerate() {
                let redis_url = format!("redis://{}:{}", node.get("host").unwrap(), node.get("port").unwrap());
                match redis::Client::open(redis_url) {
                    Ok(client) => {
                        match client.get_connection_with_timeout(Duration::new(2, 0)) {
                            Ok(mut connection) => {
                                match connection.get("ping") {
                                    Ok(response) => {
                                        println!("Connection to {} as node{}", redis_url, idx+1);
                                        redis_clients.insert(format!("node{}", idx + 1), connection);
                                        
                                    }
                                    Ok(response) => {
                                        println!("Unexpected response from Redis {}: {}", redis_url, response);
                                        
                                    }
                                    Err(e) => {
                                        println!("Redis connection failed for {}: {}", redis_url, e);
                                        if idx == 0 {
                                            println!("Primary Redis connection failed. Using in-memory store as backup.");
                                            use_redis = false;
                                        }
                                    }
                                } 
                            }
                            Err(e) => {
                                println!("Redis connection failed for {}: {}", redis_url, e);
                            }
                        }
                    }
                    Err(e) => {
                        println!("Redis connection failed for {}: {}", redis_url, e);
                    }
                }
            }
        }
        Self {
            store: store,
            use_redis: use_redis,
            redis_clients: redis_clients,
            nodes: nodes,
            ring: ring
        }
    }

    fn get_client(&self, key: &str) -> Result<Connection, Box<dyn Error>> {
        let node = self.ring.get(key);
        Ok(*self.redis_clients.get(node.unwrap()).unwrap())
    }

    fn get(&self, key: &str) -> Result<ClientKind, RedisError> {
        let client = ClientKind::RedisClient(self.get_client(key));

        if self.use_redis && client.is_some() {
            client
        }
        ClientKind::InMemoryStore(self.store.get(key).to_string())
    }

    fn set(&self, key: &str, value: &str) -> Result((), RedisError) {
        let client = self.get_client(key);

        if self.use_redis && client.is_some() {
            match client.set(key, value) {
                Ok(()) => {
                    println!("Key: {} set successfully in Redis", key);
                    Ok(())
                }
                Err(e) => {
                    println!("Failed to set key: {} in Redis", key);
                    Err(e)
                }
            }
        } else {
            println!("Using in memory store for key: {}", key);
            self.store.insert(key, value);
        }
        Ok(())
    }

    fn set_value(key: String, value: String) -> i32 {
        // Assuming kv_store is globally available as an Arc<Mutex<KVStore>>
        let mut store = kv_store.lock().unwrap();
        store.set(key, value);
        0 // Return success code
    }
    
    // Helper function to handle retries for setting a key-value pair
    fn handle_set_thread(key: String, value: String, timeout: Duration) -> Option<i32> {
        let result = Arc::new(Mutex::new(None));
    
        // Spawn the first thread to try setting the value
        let result_clone = result.clone();
        let thread = thread::spawn(move || {
            let res = set_value(key.clone(), value.clone());
            let mut result = result_clone.lock().unwrap();
            *result = Some(res);
        });
    
        // Wait for the thread to finish or timeout
        thread::sleep(timeout); // Simulate waiting for a timeout
    
        // If the thread is still alive, attempt the second thread
        if let Ok(_) = thread.join() {
            let result = result.lock().unwrap();
            return result.clone();
        }
    
        // Spawn another thread if the first attempt failed
        let result_clone = result.clone();
        let thread = thread::spawn(move || {
            let res = set_value(key.clone(), value.clone());
            let mut result = result_clone.lock().unwrap();
            *result = Some(res);
        });
    
        // Wait again for the second thread to finish or timeout
        thread::sleep(timeout); // Simulate waiting for a timeout
    
        // If the second thread completes successfully, return the result
        if let Ok(_) = thread.join() {
            let result = result.lock().unwrap();
            return result.clone();
        }
    
        // Return None if both attempts failed
        None
    }
    



    // TODO: Complete delete function
}