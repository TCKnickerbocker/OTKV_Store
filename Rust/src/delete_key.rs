// delete_key.rs
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::Duration;
use crate::kv_store::KVStore;

pub fn handle_delete_thread(key: String, kv_store: Arc<Mutex<KVStore>>, timeout: f64) -> Option<i32> {
    let key_clone = key.clone();
    let store_clone = Arc::clone(&kv_store);
    
    // First attempt
    let handle = thread::spawn(move || {
        delete_key(key_clone, store_clone)
    });

    match handle.join_timeout(Duration::from_secs_f64(timeout)) {
        Ok(result) => return Some(result),
        Err(_) => {
            // Second attempt
            let key_clone = key.clone();
            let store_clone = Arc::clone(&kv_store);
            let handle = thread::spawn(move || {
                delete_key(key_clone, store_clone)
            });

            match handle.join_timeout(Duration::from_secs_f64(timeout)) {
                Ok(result) => Some(result),
                Err(_) => None,
            }
        }
    }
}

pub fn delete_key(key: String, kv_store: Arc<Mutex<KVStore>>) -> i32 {
    // Safely delete the key from kv_store using lock
    let mut store = kv_store.lock().unwrap();
    match store.delete(&key) {
        Some(_) => {
            println!("delete res: success");
            0  // Key successfully deleted
        },
        None => {
            println!("delete res: key not found");
            -1  // Key not found
        }
    }
}
