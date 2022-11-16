use std::path::PathBuf;
use std::thread::sleep;
use std::time::Duration;

extern crate client;
use client::client_socket_stream;

extern crate testconfig;
use testconfig::TESTDATA;

use reverse_proxy::reverse_proxy_tcp;

#[test]
fn test_reverse_proxy() {
    let udp_upstream_addr = "0.0.0.0:8892".to_string();
    let multicast_addr = "224.0.0.1:8893".to_string();
    let proxy_tcp_listen_addr = "0.0.0.0:8894".to_string();
    let client_target_addr = "127.0.0.1:8892".to_string();
    let data = PathBuf::from(TESTDATA);

    // start reverse proxy and wait a moment for thread to spawn
    let _r = reverse_proxy_tcp(multicast_addr, proxy_tcp_listen_addr);
    sleep(Duration::from_millis(30));

    // send some data via the proxy
    let _c = client_socket_stream(&data, vec![client_target_addr], false);
    sleep(Duration::from_millis(15));
}