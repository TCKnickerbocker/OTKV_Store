use std::collections::HashMap;
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::Duration;

use actix_web::{guard, get, post, delete, web, App, HttpResponse, HttpServer, Responder, Result};
use serde::{Deserialize, Serialize};
use pyo3::prelude::*;
use pyo3::types::PyModule;
use pyo3::types::IntoPyDict;
use pyo3_ffi::c_str;

// Converts JSON data into this struct
#[derive(Deserialize)]
struct PostKey {
    value: String
}

#[derive(Serialize)]
struct GetResponse {
    value: String,
}

type SharedState = Arc<Mutex<HashMap<String, String>>>;

// fn call_log_operation(operation_type: String, key: String, result: &String) -> PyResult<()> {
//     Python::with_gil(|py| {

//     // imports trie_kv_store.py module
//     let trie_kv_store = c_str!(include_str!(
//         "./trie_kv_store.py"
//     ));
//     PyModule::from_code(py, trie_kv_store, c_str!("trie_kv_store"), c_str!("trie_kv_store"))?;

//     let code = c_str!(include_str!(
//         "./logger.py"
//     ));
//     let logger = PyModule::from_code(py, code, c_str!("logger.py"), c_str!("logger"))?;

//     // If result is successful, pass in success to log_operation
//     if result == "0" {
//         logger.getattr("log_operation")?.call1((operation_type, key, "success".to_string()))?;
//     } else {
//         logger.getattr("log_operation")?.call1((operation_type, key, "timeout".to_string()))?;
//     }
    

//     Ok(())
//     })
// }

#[post("/{key}")]
pub async fn set_value_app(state: web::Data<SharedState>, key: web::Path<String>, data: web::Json<PostKey>) -> impl Responder {
    let key = key.into_inner();
    let value = &data.value;
    let mut map = state.lock().unwrap();
    map.insert(key.clone(), value.clone());

    // match call_set_value(key.to_string(), value.to_string()) {
    //     Ok(response) => {
    //         match call_log_operation("set".to_string(), key.to_string(), &response.to_string()) {
    //             Ok(_) => println!("Successful Rust Log Operation"),
    //             Err(e) => println!("Unsuccessful Rust Log Operation Error: {}", e)
    //         }
            
    //         if response != "0" {
    //             return HttpResponse::GatewayTimeout().body("Timeout setting value")
    //         }
    //     }
    //     Err(e) => {
    //         println!("Error in post: {}", e);
    //     }
    // }
    
    HttpResponse::Ok()
        .body((format!("Value for key '{}' set successfully.", key)))
}

fn get_value(key: &str) -> String {
    // Simulate some computation or fetching a value
    format!("Value for {}", key)
}

#[get("/{key}")]
pub async fn get_value_app(state: web::Data<SharedState>, key: web::Path<String>) -> impl Responder {
    let key = key.into_inner();
    let map = state.lock().unwrap();
    if let Some(value) = map.get(&key) {
        return HttpResponse::Ok().body(format!("Key: {}, Value: {}", key, value))
    } else {
        return HttpResponse::NotFound().body("Key not found")
    }
}

#[delete("/{key}")]
pub async fn delete_value_app(state: web::Data<SharedState>, key: web::Path<String>) -> impl Responder {
    let key = key.into_inner();
    let mut map = state.lock().unwrap();
    if map.remove(&key).is_some() {
        return HttpResponse::Ok().body(format!("Key {} deleted", key))
    } else {
        return HttpResponse::NotFound().body("Key not found")
    }

    // match call_delete_key(key.to_string()) {
    //     // TODO: Fix this structure, we need 3 cases where one timeouts, one DNE, and one is successful
    //     Ok(response) => {
    //         println!("Response: {}", response);
    //         if response == "-1" {
    //             match call_log_operation("timeout".to_string(), "".to_string(), &"".to_string()) {
    //                 Ok(_) => println!("Rust Log Timeout Operation"),
    //                 Err(e) => println!("Unsuccessful Rust Log Operation Error: {}", e)
    //             }

    //             return HttpResponse::GatewayTimeout().body("Timeout setting value")
    //         } else if response == "0" {
    //             match call_log_operation("delete".to_string(), key.to_string(), &"did not exist".to_string()) {
    //                 Ok(_) => println!("Rust Log Delete DNE Operation"),
    //                 Err(e) => println!("Unsuccessful Rust Log Operation Error: {}", e)
    //             }

    //             return HttpResponse::NotFound().body(format!("Key '{}' did not exist", key))
    //         } else {
    //             match call_log_operation("delete".to_string(), key.to_string(), &"success".to_string()) {
    //                 Ok(_) => println!("Successful Rust Log Operation"),
    //                 Err(e) => println!("Unsuccessful Rust Log Operation Error: {}", e)
    //             }

    //             return HttpResponse::Ok().body(format!("Key '{}' deleted successfully.", key))
    //         }
    //     }
    //     Err(e) => {
    //         println!("Error in delete: {}", e);
    //     }
    // }

    HttpResponse::Ok().body("In call_delete_key, should not have reached this line")
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    let state: SharedState = Arc::new(Mutex::new(HashMap::new()));

    HttpServer::new(move || {
        App::new()
            .app_data(web::Data::new(state.clone()))
            .service(set_value_app)
            .service(get_value_app)
            .service(delete_value_app)
    })
    .bind("0.0.0.0:8080")?
    .run()
    .await
}