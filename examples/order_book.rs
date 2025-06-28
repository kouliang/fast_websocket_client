// try this example with
// `cargo run --example order_book`

use fast_websocket_client::WebSocket;

#[tokio::main(flavor = "current_thread")]
async fn main() -> Result<(), fast_websocket_client::WebSocketClientError> {

    let ws = WebSocket::new_with_proxy("wss://stream.binance.com:9443/ws/bnbbtc@depth", "127.0.0.1:7890", |_| async {
        println!("[OPEN]");
    }).await?;

    ws.on_error(|message| async move {
        println!("[ERROR] {}", message);
    }).await;

    ws.on_message(|message| async move {
        println!("[MESSAGE] {}", message);
    }).await;

    let _ = ws.task_handle.await;
    Ok(())
}