use std::collections::HashMap;
use std::sync::{Arc, RwLock};

use actix_web::{get, post, delete, web, App, HttpResponse, HttpServer, Responder};
use serde::Deserialize;
use tokio::task;
use dashmap::DashMap;

// Converts JSON data into this struct
#[derive(Deserialize)]
struct PostKey {
    value: String
}

type SharedState = Arc<RwLock<DashMap<String, String>>>;

// TODO: Remove Clones
#[post("/{key}")]
pub async fn set_value_app(state: web::Data<SharedState>, key: web::Path<String>, data: web::Json<PostKey>) -> impl Responder {
    let key = key.into_inner();
    let value = data.into_inner().value;
    // let key_clone = &key;
    // let val_clone = &value;

    let state_clone = Arc::clone(&state);

    let task = tokio::spawn(async move {
        let mut state = state_clone.write().unwrap();
        let key_clone = key.clone();
        let val_clone = value.clone();
        if state.contains_key(&key) {
            return ("false".to_string(), key_clone)
        }
        // println!("Key-value pair inserted asynchronously: ({}, {})", &key, &value);
        state.insert(key.clone(), value.clone());  // Store the key-value pair
        return (val_clone, key_clone)
    });

    match task.await {
        Ok((value, key)) => {
            if value != "false" {
                return HttpResponse::Ok().body(format!("Received POST request: ({}, {})", &key, &value))
            } else {
                return HttpResponse::InternalServerError().body(format!("Key-Value pair is already present: ({}, {})", key, value))
            }
        }
        Err(e) => return HttpResponse::InternalServerError().body(format!("Ran into error in POST: {}", e))
    }

    
}

#[get("/{key}")]
pub async fn get_value_app(state: web::Data<SharedState>, key: web::Path<String>) -> impl Responder {
    let key = key.into_inner();

    let state_clone = Arc::clone(&state);

    let task = tokio::spawn(async move {
        let state = state_clone.write().unwrap();
        state.contains_key(&key)
    });

    match task.await {
        Ok(key) => {
            if key {
                return HttpResponse::Ok().body(format!("Found Key: {}", key))
            } else {
                return HttpResponse::NotFound().body(format!("Was not able to find Key: {}", key))
            }
        }
        Err(_) => HttpResponse::InternalServerError().body("Error in GET key"),
    }
}

#[delete("/{key}")]
pub async fn delete_value_app(state: web::Data<SharedState>, key: web::Path<String>) -> impl Responder {
    let key = key.into_inner();
    let new_key = key.clone();

    let state_clone = Arc::clone(&state);

    let task = tokio::spawn(async move {
        let mut state = state_clone.write().unwrap();
        state.remove(&key)
    });

    match task.await {
        Ok(value) => {
            if value.is_some() {
                return HttpResponse::Ok().body(format!("Found Key: {}", &new_key))
            } else {
                return HttpResponse::NotFound().body(format!("Was not able to find Key: {}", &new_key))
            }
        }
        Err(_) => HttpResponse::InternalServerError().body("Error in GET key"),
    }
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    let shared_state: SharedState = Arc::new(RwLock::new(DashMap::new()));

    let state1 = shared_state.clone();
    let s1 = HttpServer::new(move || {
        App::new()
            .app_data(web::Data::new(state1.clone()))
            .service(set_value_app)
            .service(get_value_app)
            .service(delete_value_app)
    })
    .bind(format!("0.0.0.0:{}", 8080))?
    .run();

    task::spawn(s1);

    let state2 = shared_state.clone();
    let s2 = HttpServer::new(move || {
        App::new()
            .app_data(web::Data::new(state2.clone()))
            .service(set_value_app)
            .service(get_value_app)
            .service(delete_value_app)
    })
    .bind(format!("0.0.0.0:{}", 8081))?
    .run();

    task::spawn(s2);

    let state2 = shared_state.clone();
    let s2 = HttpServer::new(move || {
        App::new()
            .app_data(web::Data::new(state2.clone()))
            .service(set_value_app)
            .service(get_value_app)
            .service(delete_value_app)
    })
    .bind(format!("0.0.0.0:{}", 8082))?
    .run();

    task::spawn(s2);

    loop {
        tokio::time::sleep(tokio::time::Duration::from_secs(1)).await;
    }
}