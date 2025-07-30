// try this example with
// `cargo run --example order_book`
// https://developers.binance.com/docs/zh-CN/binance-spot-api-docs/web-socket-streams#%E5%A6%82%E4%BD%95%E6%AD%A3%E7%A1%AE%E5%9C%A8%E6%9C%AC%E5%9C%B0%E7%BB%B4%E6%8A%A4%E4%B8%80%E4%B8%AAorder-book%E5%89%AF%E6%9C%AC

use fast_websocket_client::WebSocket;
use serde::{Deserialize, Serialize};
use anyhow::{Context, Result};
use lazy_static::lazy_static;
use std::sync::Arc;
use tokio::sync::Mutex;

// 定义订单簿更新事件的结构
#[derive(Debug, Serialize, Deserialize, Default)]
pub struct OrderBookUpdate {
    pub e: String,  // 事件类型
    pub E: u64,     // 事件时间
    pub s: String,  // 交易对
    pub U: u64,     // 首次更新ID
    pub u: u64,     // 最后更新ID
    pub b: Vec<Vec<String>>, // 买单更新 [价格, 数量]
    pub a: Vec<Vec<String>>, // 卖单更新 [价格, 数量]
}

// 定义订单簿结构
#[derive(Debug, Serialize, Deserialize, Default)]
pub struct OrderBook {
    pub lastUpdateId: u64,
    pub bids: Vec<Vec<String>>, // 买单更新 [价格, 数量]
    pub asks: Vec<Vec<String>>, // 卖单更新 [价格, 数量]
}

lazy_static! {
    static ref ORDER_BOOK: Arc<Mutex<OrderBook>> = Arc::new(Mutex::new(OrderBook::default()));
}

#[tokio::main(flavor = "current_thread")]
async fn main() -> Result<()> {
    // 如果不使用代理，proxy传入空串
    let ws = WebSocket::new_with_proxy("wss://stream.binance.com:9443/ws/bnbbtc@depth", "", |_| async {
        println!("[OPEN]");
    }).await?;

    ws.on_error(|message| async move {
        println!("[ERROR] {}", message);
    }).await;

    ws.on_message(|message| async move {
        println!("[MESSAGE]========================");
        match serde_json::from_str::<OrderBookUpdate>(&message) {
            Ok(update) => {
                let _ = update_order_book(update, ORDER_BOOK.clone()).await;
            },
            Err(e) => {
                println!("Failed to parse order book update: {}", e);
            }
        }
    }).await;

    let _ = ws.task_handle.await;
    Ok(())
}

async fn update_order_book(update: OrderBookUpdate, order_book:Arc<Mutex<OrderBook>>) -> Result<()> {

    println!("update U: {}", update.U);
    println!("update u: {}", update.u);    

    // 1. 不满足以下条件说明快照损坏需要重新构建
    //    lastUpdateId   U<lastUpdateId+1>   u
    let mut order_book_guard = order_book.lock().await;
    if update.U > order_book_guard.lastUpdateId+1 {
        println!("reset order book ❌❌❌❌❌❌❌❌❌❌❌");
        let new_order_book = get_order_book().await?;
        *order_book_guard = new_order_book;
    }
    println!("order_book lastUpdateId: {}", order_book_guard.lastUpdateId);
    
    // 2. 满足一下条件时更新快照
    if update.U == order_book_guard.lastUpdateId+1 {
        println!("do update ✅✅✅✅✅✅✅✅");
        
        // 将order book更新 ID 设置为处理过event中的最后一次更新 ID (u)。
        order_book_guard.lastUpdateId = update.u;

        // 如果order book中不存在价位，则插入新的数量。
        // TODO

        // 如果数量为零，则从order book中删除此价位。
        // TODO
    } else {
        println!("waiting for the next update ... ");
    }
    Ok(())
}

// 如果快照中的 lastUpdateId 一定大于 update_id
async fn get_order_book() -> Result<OrderBook> {
    let request_url = "https://api.binance.com/api/v3/depth?symbol=BNBBTC&limit=5000";
    let body: String = reqwest::get(request_url).await?
        .text().await?;

    let order_book = serde_json::from_str::<OrderBook>(&body).context("Failed to parse JSON")?;
   
    Ok(order_book)
}