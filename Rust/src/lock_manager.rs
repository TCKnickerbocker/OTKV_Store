use std::sync::{Arc, Mutex};
use lazy_static::lazy_static;

// Using lazy_static to create a global, thread-safe lock
lazy_static! {
    pub static ref KV_LOCK: Arc<Mutex<()>> = Arc::new(Mutex::new(()));
}

// Example of using the lock
fn example_lock_usage() {
    // Clone the lock for use in a thread
    let lock_clone = Arc::clone(&KV_LOCK);
    
    std::thread::spawn(move || {
        // Acquire the lock
        let _guard = lock_clone.lock().unwrap();
        
        // Critical section: Perform operations that require exclusive access
        println!("Thread has acquired the lock");
        
        // Lock is automatically released when _guard goes out of scope
    });
}

// If you want a function to wrap lock acquisition
pub fn with_lock<F, R>(f: F) -> R 
where 
    F: FnOnce() -> R 
{
    let _lock = KV_LOCK.lock().unwrap();
    f()
}
