# -*- coding: utf-8 -*-
import socket

def start_server(host='127.0.0.1', port=12345):
    # 创建 socket 对象
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # 设置选项，允许重新使用地址，这在重启服务时可以避免等待
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # 绑定地址和端口
    server_socket.bind((host, port))

    # 开始监听连接请求
    server_socket.listen(5)
    print(f"Server listening on {host}:{port}")

    while True:
        # 接受客户端连接
        client_socket, client_address = server_socket.accept()
        print(f"Connected to {client_address}")

        # 接收数据
        while True:
            data = client_socket.recv(1024)
            if not data:
                break  # 如果没有接收到数据，跳出循环
            print(f"Received from {client_address}: {data.decode()}")
            # 发送数据
            client_socket.sendall(data)

        # 断开客户端连接
        client_socket.close()
        print(f"Connection with {client_address} closed")

if __name__ == '__main__':
    start_server()
