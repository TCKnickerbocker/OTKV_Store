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

fn call_set_value(key: String, value: String) -> PyResult<(String)> {
    Python::with_gil(|py| {

    // imports kv_store.py module
    let kv_store = c_str!(include_str!(
        "./kv_store.py"
    ));
    PyModule::from_code(py, kv_store, c_str!("kv_store"), c_str!("kv_store"))?;

    // imports lock_manager.py module
    let lock_manager = c_str!(include_str!(
        "./lock_manager.py"
    ));
    PyModule::from_code(py, lock_manager, c_str!("lock_manager"), c_str!("lock_manager"))?;

    let code = c_str!(include_str!(
        "./set_value.py"
    ));
    let set_value = PyModule::from_code(py, code, c_str!("set_value.py"), c_str!("set_value"))?;

    // Calling handle_set_thread
    let result = set_value.getattr("handle_set_thread")?.call1((key, value))?;

    // Extracting the data returned from handle_set_thread
    let response: String = result.extract()?;

    Ok(response)
    })
}

fn call_log_operation(operation_type: String, key: String, result: &String) -> PyResult<()> {
    Python::with_gil(|py| {

    // imports kv_store.py module
    let kv_store = c_str!(include_str!(
        "./kv_store.py"
    ));
    PyModule::from_code(py, kv_store, c_str!("kv_store"), c_str!("kv_store"))?;

    let code = c_str!(include_str!(
        "./logger.py"
    ));
    let logger = PyModule::from_code(py, code, c_str!("logger.py"), c_str!("logger"))?;

    // If result is successful, pass in success to log_operation
    if result == "0" {
        logger.getattr("log_operation")?.call1((operation_type, key, "success".to_string()))?;
    } else {
        logger.getattr("log_operation")?.call1((operation_type, key, "timeout".to_string()))?;
    }
    

    Ok(())
    })
}

#[post("/{key}")]
pub async fn set_value_app(key: web::Path<String>, data: web::Json<PostKey>) -> impl Responder {
    let key = key.into_inner();
    // TODO: if 'value' not in data:
    // return jsonify({"error": "Missing 'value' in request body"}), 400
    let value = &data.value;

    match call_set_value(key.to_string(), value.to_string()) {
        Ok(response) => {
            match call_log_operation("set".to_string(), key.to_string(), &response.to_string()) {
                Ok(_) => println!("Successful Rust Log Operation"),
                Err(e) => println!("Unsuccessful Rust Log Operation Error: {}", e)
            }
            
            if response != "0" {
                return HttpResponse::GatewayTimeout().body("Timeout setting value")
            }
        }
        Err(e) => {
            println!("Error here: {}", e);
        }
    }
    
    HttpResponse::Ok()
        .body((format!("Value for key '{}' set successfully.", key)))
}

fn call_get_value(key: String) -> PyResult<(String)> {
    Python::with_gil(|py| {

    // imports kv_store.py module
    let kv_store = c_str!(include_str!(
        "./kv_store.py"
    ));
    PyModule::from_code(py, kv_store, c_str!("kv_store"), c_str!("kv_store"))?;

    let code = c_str!(include_str!(
        "./get_value.py"
    ));
    let get_value = PyModule::from_code(py, code, c_str!("get_value.py"), c_str!("get_value"))?;

    // Calling handle_get_thread
    let result = get_value.getattr("handle_get_thread")?.call1((key,))?;

    // Extracting the data returned from handle_get_thread
    let response: String = result.extract()?;

    Ok(response)
    })
}

#[get("/{key}")]
pub async fn get_value_app(key: web::Path<String>) -> impl Responder {

    match call_get_value(key.to_string()) {
        Ok(response) => {
            match call_log_operation("get".to_string(), key.to_string(), &response) {
                Ok(_) => println!("Successful Rust Log Operation"),
                Err(e) => println!("Unsuccessful Rust Log Operation Error: {}", e)
            }
            
            if response == "-1".to_string() {
                return HttpResponse::NotFound().body(format!("Key '{}' not found", key));
            } else {
                let obj = GetResponse {
                    value: response
                };
                return HttpResponse::Ok()
                    .json(web::Json(obj))
            }
        }
        Err(e) => {
            println!("Error here: {}", e);
        }
    }

    HttpResponse::Ok().body("In call_get_value, should not have reached this line")
}

fn call_delete_key(key: String) -> PyResult<(String)> {
    Python::with_gil(|py| {

    // imports kv_store.py module
    let kv_store = c_str!(include_str!(
        "./kv_store.py"
    ));
    PyModule::from_code(py, kv_store, c_str!("kv_store"), c_str!("kv_store"))?;

    // imports lock_manager.py module
    let lock_manager = c_str!(include_str!(
        "./lock_manager.py"
    ));
    PyModule::from_code(py, lock_manager, c_str!("lock_manager"), c_str!("lock_manager"))?;

    let code = c_str!(include_str!(
        "./delete_key.py"
    ));
    let set_value = PyModule::from_code(py, code, c_str!("delete_key.py"), c_str!("delete_key"))?;

    // Calling handle_set_thread
    let result = set_value.getattr("handle_delete_thread")?.call1((key,))?;

    // Extracting the data returned from handle_set_thread
    let response: String = result.extract()?;

    Ok(response)
    })
}

#[delete("/{key}")]
pub async fn delete_value_app(key: web::Path<String>) -> impl Responder {
    let key = key.into_inner();
    println!("{}", key.to_string());

    match call_delete_key(key.to_string()) {
        // TODO: Fix this structure, we need 3 cases where one timeouts, one DNE, and one is successful
        Ok(response) => {
            println!("Response: {}", response);
            if response == "-1" {
                match call_log_operation("timeout".to_string(), "".to_string(), &"".to_string()) {
                    Ok(_) => println!("Rust Log Timeout Operation"),
                    Err(e) => println!("Unsuccessful Rust Log Operation Error: {}", e)
                }

                return HttpResponse::GatewayTimeout().body("Timeout setting value")
            } else if response == "0" {
                match call_log_operation("delete".to_string(), key.to_string(), &"did not exist".to_string()) {
                    Ok(_) => println!("Rust Log Delete DNE Operation"),
                    Err(e) => println!("Unsuccessful Rust Log Operation Error: {}", e)
                }

                return HttpResponse::NotFound().body(format!("Key '{}' did not exist", key))
            } else {
                match call_log_operation("delete".to_string(), key.to_string(), &"success".to_string()) {
                    Ok(_) => println!("Successful Rust Log Operation"),
                    Err(e) => println!("Unsuccessful Rust Log Operation Error: {}", e)
                }

                return HttpResponse::Ok().body(format!("Key '{}' deleted successfully.", key))
            }
        }
        Err(e) => {
            println!("Error here: {}", e);
        }
    }

    HttpResponse::Ok().body("In call_delete_key, should not have reached this line")
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {

    HttpServer::new(move || {
        App::new()
            .service(set_value_app)
            .service(get_value_app)
            .service(delete_value_app)
    })
    .bind("0.0.0.0:8080")?
    .run()
    .await
}