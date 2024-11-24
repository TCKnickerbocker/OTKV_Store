use actix_web::{guard, get, post, delete, web, App, HttpResponse, HttpServer, Responder, Result};
use serde::{Deserialize, Serialize};
mod kv_store;
use kv_store::KVStore;

// Converts JSON data into this struct
#[derive(Deserialize)]
struct PostKey {
    key: String,
    value: String
}

#[derive(Serialize)]
struct GetKey {
    key: String,
}

#[post("/{key}")]
pub async fn set_value_app(key: web::Path<String>, data: web::Json<PostKey>) -> impl Responder {
    let key = key.into_inner();
    let value = &data.value;
    key
}

#[get("/{key}")]
pub async fn get_value_app(key: web::Path<String>) -> Result<impl Responder> {
    let obj = GetKey {
        key: key.to_string()
    };

    Ok(web::Json(obj))
}

#[delete("/{key}")]
pub async fn delete_value_app(key: web::Path<String>) -> impl Responder {
    let key = key.into_inner();
    key
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    let kv_store = KVStore::new();

    HttpServer::new(move || {
        App::new()
            .app_data(web::Data::new(kv_store.clone()))
            .service(set_value_app)
            .service(get_value_app)
            .service(delete_value_app)
    })
    .bind("0.0.0.0:8080")?
    .run()
    .await
}