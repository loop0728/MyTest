# -*- coding: utf-8 -*-
import socket

def start_client(host='127.0.0.1', port=12345):
    # 创建 socket 对象
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # 连接到服务端
    client_socket.connect((host, port))
    
    try:
        # 发送数据
        message = "Hello, Server!"
        client_socket.sendall(message.encode())
        
        # 接收响应
        response = client_socket.recv(1024)
        print(f"Received: {response.decode()}")
        
    finally:
        # 关闭连接
        client_socket.close()

if __name__ == '__main__':
    start_client()