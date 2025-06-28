// try this example with
// `cargo run --example wss_client`

use fast_websocket_client::WebSocket;
use tokio::time::{Duration, sleep};

#[tokio::main(flavor = "current_thread")]
async fn main() -> Result<(), fast_websocket_client::WebSocketClientError> {

    let ws = WebSocket::new_with_proxy("wss://stream.binance.com:9443/ws/bnbbtc@depth", "127.0.0.1:7890", |_| async {
        println!("[OPEN]");
    }).await?;

    ws.on_close(|_| async move {
        println!("[CLOSE] WebSocket connection closed.");
    })
    .await;
    ws.on_message(|message| async move {
        println!("[MESSAGE] {}", message);
    })
    .await;

    ws.on_error(|message| async move {
        println!("[ERROR] {}", message);
    })
    .await;

    sleep(Duration::from_secs(10)).await;
    // for i in 1..5 {
    //     let message = format!("#{}", i);
    //     if let Err(e) = ws.send(&message).await {
    //         eprintln!("[ERROR] Send error: {:?}", e);
    //         break;
    //     }
    //     println!("[SEND] {}", message);
    //     sleep(Duration::from_secs(5)).await;
    // }

    ws.close().await;
    ws.await_shutdown().await;
    Ok(())
}