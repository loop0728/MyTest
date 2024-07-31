import sys
import socket
import time
from PythonScripts.variables import net_connect_port

def client_send_msg(send_msg):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('localhost',int(net_connect_port)))
    print("send_msg:", send_msg)
    client.send(send_msg.encode('utf-8'))
    response = client.recv(1024)
    if response.decode('utf-8') == "OK":
        return 0
    return 255


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "exit":
        ret = client_send_msg(sys.argv[1])
        sys.exit(ret)

    if len(sys.argv) < 3:
        print("Usage: python client.py <scripts> <case>")
        sys.exit(255)

    message = sys.argv[1] + "+" + sys.argv[2]
    #print("message:", message)

    ret = client_send_msg(message)
    #print("client_send_msg ret:", ret)
    sys.exit(ret)
