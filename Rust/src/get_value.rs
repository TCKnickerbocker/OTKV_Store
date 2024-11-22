use std::sync::{Arc, Mutex};
use std::time::Duration;
use std::thread;

use crate::kv_store::KvStore;  // Assuming KvStore is in kv_store.rs

pub fn handle_get_thread(kv_store: &Arc<Mutex<KvStore>>, key: &str, timeout: Duration) -> Option<String> {
    let result = Arc::new(Mutex::new(None));
    
    let result_clone = Arc::clone(&result);
    let key_clone = key.to_string();
    let kv_store_clone = Arc::clone(kv_store);

    let handle = thread::spawn(move || {
        let value = get_value(&kv_store_clone, &key_clone);
        let mut result = result_clone.lock().unwrap();
        *result = Some(value);
    });

    // Wait for the thread to complete or timeout
    if handle.join_timeout(timeout).is_err() {
        // If first thread times out, spawn another
        let result_clone2 = Arc::clone(&result);
        let key_clone2 = key.to_string();
        let kv_store_clone2 = Arc::clone(kv_store);

        let handle2 = thread::spawn(move || {
            let value = get_value(&kv_store_clone2, &key_clone2);
            let mut result = result_clone2.lock().unwrap();
            *result = Some(value);
        });

        // Wait for the second thread
        if handle2.join_timeout(timeout).is_err() {
            return None;
        }
    }

    // Retrieve and return the result
    let result = result.lock().unwrap();
    result.clone()
}

pub fn get_value(kv_store: &Arc<Mutex<KvStore>>, key: &str) -> Option<String> {
    // Retrieve value from kv_store
    let kv_store_lock = kv_store.lock().unwrap();
    kv_store_lock.get(key)
}

// Example usage in main or another function
fn example_usage() {
    let kv_store = Arc::new(Mutex::new(KvStore::new(3, true, 6379)));
    
    // Set a value first
    {
        let mut store = kv_store.lock().unwrap();
        store.set("test_key", "test_value").unwrap();
    }

    // Get the value with retry mechanism
    let result = handle_get_thread(&kv_store, "test_key", Duration::from_millis(10));
    
    match result {
        Some(value) => println!("Retrieved value: {}", value),
        None => println!("Failed to retrieve value"),
    }
}
