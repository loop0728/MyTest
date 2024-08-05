# -*- coding: utf-8 -*-
import socket

def start_client(host='127.0.0.1', port=12345):
    """启动客户端"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((host, port))
        
        while True:
            message = input("Enter message to send (or 'quit' to exit): ")
            if message.lower() == 'quit':
                break
            client_socket.sendall(message.encode())
            
            # 接收服务端的响应
            response = client_socket.recv(1024)
            print(f"Received: {response.decode()}")

if __name__ == '__main__':
    start_client()