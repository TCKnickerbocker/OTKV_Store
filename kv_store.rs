use hashring::HashRing;
use std::collections::HashMap;
use redis::{Client, Commands, Connection, ConnectionLike, RedisError};
use std::env;
use std::time::Duration;
use std::error::Error;

pub struct KVStore {
    store: HashMap<String, String>,
    ring: HashRing<String>,
}

impl KVStore {
    fn new(num_nodes: u8, use_redis: bool, base_port: u16) -> Self {
        let mut store = HashMap::new();

        // match env::var("DOCKER_ENV") {
        //     Ok(docker) => {
        //         for i in 0..num_nodes {
        //             let mut node: HashMap<String, u16> = HashMap::new();
        //             node.insert(format!("redis-{}", i+1), base_port);
        //             nodes.push(node);
        //         }
        //     }
        //     Err(e) => {
        //         for i in 0..num_nodes {
        //             let mut node: HashMap<String, u16> = HashMap::new();
        //             node.insert(redis_host, base_port+(i as u16));
        //             nodes.push(node);
        //         }
        //     }
        // }

        // let mut node_names: Vec<String> = Vec::new();

        // for i in 0..num_nodes {
        //     node_names.push(format!("node{}", i+1))
        // }

        // let mut ring = HashRing::new();

        // for name in node_names {
        //     ring.add(name);
        // }
    }

    fn get(&self, key: &str) -> Result<String> {
        match 
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
    fn handle_set_thread(&self, key: String, value: String, timeout: Duration) -> Option<i32> {
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
            let res = self.set_value(key.clone(), value.clone());
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