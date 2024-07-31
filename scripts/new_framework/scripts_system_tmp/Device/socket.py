#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @author      : SigmaStar
# @date        : 2024/07/24 22:43:44
# @file        : socket.py
# @description :

import socket

class SocketDevice():

    def __init__(self, name, host, port):
        self.name = name
        self.host = host
        self.port = port
        self.socket_connection = None

    def connect(self):
        self.socket_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_connection.connect((self.host, self.port))
        print(f"Socket {self.name} Connect")

    def disconnect(self):
        if self.socket_connection:
            self.socket_connection.close()
            print(f"Socket {self.name} disconnect")

    def send_data(self, data):
        if self.socket_connection:
            self.socket_connection.sendall(data.encode('utf-8'))
        else:
            print("Socket not connect, cant't send.")