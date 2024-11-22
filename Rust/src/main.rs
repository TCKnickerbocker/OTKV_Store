use actix_web::{HttpServer, App};
use clap::Parser;
use std::thread;
use std::sync::mpsc;

mod endpoints;
// mod handlers;
mod logger;

#[derive(Parser, Debug)]
#[command(author, version, about, long_about = None)]
struct Args {
    /// Number of Redis nodes to create
    #[arg(long, default_value_t = 3)]
    nodes: u8,

    /// Base port number for Redis nodes
    #[arg(long, default_value_t = 6380)]
    base_port: u16,

    /// Port to run the Actix application
    #[arg(long, default_value_t = 8080)]
    port: u16,
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    // Parse command-line arguments
    let args = Args::parse();

    // Create a channel for log queue management
    let (tx, rx) = mpsc::channel();

    // Start the logging pulse thread
    let pulse_thread = thread::spawn(move || {
        logger::log_entire_store(rx);
    });

    // Prepare server shutdown channel
    let (shutdown_tx, shutdown_rx) = mpsc::channel();

    // Spawn server
    let server = HttpServer::new(|| {
        App::new()
            .configure(endpoints::configure_routes)
    })
    .bind(("0.0.0.0", args.port))?
    .run();

    // Handle graceful shutdown
    tokio::spawn(async move {
        shutdown_rx.recv().unwrap();
        server.stop(true).await;
    });

    // Wait for server to complete
    let server_result = server.await;

    // Signal log thread to stop
    tx.send(()).expect("Failed to send shutdown signal to log thread");
    
    // Wait for pulse thread to finish
    pulse_thread.join().expect("Failed to join pulse thread");

    server_result
}
