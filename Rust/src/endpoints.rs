use actix_web::{
    web::{self, Path, Json},
    HttpResponse, 
    Responder, 
    get, 
    post, 
    delete
};
use serde::{Deserialize, Serialize};

// Update these imports to use local modules
use crate::kv_store::{
    handle_get_thread, 
    handle_set_thread, 
    handle_delete_thread
};
use crate::logger::log_operation;


#[derive(Deserialize)]
pub struct ValueRequest {
    value: String,
}

#[derive(Serialize)]
pub struct SuccessResponse {
    message: String,
}

#[derive(Serialize)]
pub struct ValueResponse {
    value: String,
}

// Set a key-value pair
#[post("/{key}")]
pub async fn set_value_handler(
    key: Path<String>, 
    request: Json<ValueRequest>
) -> impl Responder {
    // Call handler, return appropriately
    let res = handle_set_thread(&key, &request.value);
    
    log_operation("set", &key, if res.is_some() { "success" } else { "timeout" });
    
    match res {
        Some(_) => HttpResponse::Ok().json(SuccessResponse {
            message: format!("Value for key '{}' set successfully.", key)
        }),
        None => HttpResponse::GatewayTimeout().json(serde_json::json!({
            "error": "Timeout setting value"
        }))
    }
}

// Get the value for a key
#[get("/{key}")]
pub async fn get_value_handler(
    key: Path<String>
) -> impl Responder {
    // Get result, return appropriately
    let res = handle_get_thread(&key);
    
    log_operation("get", &key, if res.is_some() { "success" } else { "not found" });
    
    match res {
        Some(value) => HttpResponse::Ok().json(ValueResponse { value }),
        None => HttpResponse::NotFound().json(serde_json::json!({
            "error": format!("Key '{}' not found", key)
        }))
    }
}

// Delete a key
#[delete("/{key}")]
pub async fn delete_value_handler(
    key: Path<String>
) -> impl Responder {
    // Get result, return appropriately  
    let res = handle_delete_thread(&key);
    
    match res {
        Some(0) => {
            log_operation("delete", &key, "success");
            HttpResponse::Ok().json(SuccessResponse {
                message: format!("Key '{}' deleted successfully.", key)
            })
        },
        Some(-1) => {
            log_operation("delete", &key, "did not exist");
            HttpResponse::NotFound().json(serde_json::json!({
                "error": format!("Key '{}' did not exist", key)
            }))
        },
        None => {
            log_operation("timeout", "", "");
            HttpResponse::GatewayTimeout().json(serde_json::json!({
                "error": "Timeout deleting key"
            }))
        }
    }
}

// Configure routes
pub fn configure_routes(cfg: &mut web::ServiceConfig) {
    cfg.service(
        web::scope("/")
            .service(set_value_handler)
            .service(get_value_handler)
            .service(delete_value_handler)
    );
}

// Optional: Main server setup (if you want it in this file)
pub async fn start_server() -> std::io::Result<()> {
    HttpServer::new(|| {
        App::new()
            .configure(configure_routes)
    })
    .bind("127.0.0.1:8080")?
    .run()
    .await
}

