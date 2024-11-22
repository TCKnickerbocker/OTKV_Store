// set_value.rs
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::Duration;
use crate::kv_store::KVStore;

pub fn handle_set_thread(
    key: String, 
    value: String, 
    kv_store: Arc<Mutex<KVStore>>, 
    timeout: f64
) -> Option<i32> {
    let key_clone = key.clone();
    let value_clone = value.clone();
    let store_clone = Arc::clone(&kv_store);

    // First attempt
    let handle = thread::spawn(move || {
        set_value(key_clone, value_clone, store_clone)
    });

    match handle.join_timeout(Duration::from_secs_f64(timeout)) {
        Ok(result) => Some(result),
        Err(_) => {
            // Second attempt
            let key_clone = key.clone();
            let value_clone = value.clone();
            let store_clone = Arc::clone(&kv_store);
            let handle = thread::spawn(move || {
                set_value(key_clone, value_clone, store_clone)
            });

            match handle.join_timeout(Duration::from_secs_f64(timeout)) {
                Ok(result) => Some(result),
                Err(_) => None,
            }
        }
    }
}

pub fn set_value(key: String, value: String, kv_store: Arc<Mutex<KVStore>>) -> i32 {
    // Safely set key-value pair using lock
    let mut store = kv_store.lock().unwrap();
    store.set(key, value);
    // TODO: Forward to next in chain
    0
}
