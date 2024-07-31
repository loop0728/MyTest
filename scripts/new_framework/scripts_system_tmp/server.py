import sys
import time
import socket
import threading
import json
import re
import numpy as np
from concurrent.futures import ThreadPoolExecutor

from PythonScripts.variables import net_connect_port, log_path, uart_port, relay_port, dev_uart
from PythonScripts.logger import logger
from Device.uartlog_contrl import SerialDevice
from Device.rs232_contrl import rs232_contrl

class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, bytes):
            return str(obj, encoding='utf-8')
        return json.JSONEncoder.default(self, obj)

class server_handle():
    def __init__(self, max_workers=5, listen_client_num=5, rev_max_datalen=1024):
        self.server_handler = None
        self.server_thread_running = True
        self.max_workers = max_workers
        self.listen_client_num = listen_client_num
        self.rev_max_datalen = rev_max_datalen
        self.dev_names = ['serial']
        self.cur_board_state = 'Unknow'
        self.delimiter = 'mstar'
        self.host = 'localhost'
        self.port = int(net_connect_port)
        # 创建 Socket 对象
        self.thread_pool = ThreadPoolExecutor(self.max_workers)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.server_socket:
           self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def device_init(self):
        if 'serial' in self.dev_names:
            self.serial_init()
        elif 'socket' in self.dev_names:
            pass
            # self.socket_init()

    def serial_init(self):
        self.serial_port = SerialDevice(uart_port, log_path)
        self.serial_port.connect()

    def device_deinit(self):
        if 'serial' in self.dev_names:
            self.serial_deinit()
        elif 'socket' in self.dev_names:
            pass

    def serial_deinit(self):
        self.serial_port.disconnect()

    def send_msg_to_client(self, client, msg):
        """
        发送消息, 保证发送消息时统一格式

        Args:
            client: Class: socket 对象
            msg: dict: 发送的消息内容

        Returns:
            NA
        """
        msg = json.dumps(msg)
        full_msg = f"{msg}mstar"
        client.sendall(full_msg.encode('utf-8'))

    def response_msg_to_client(self, client, status):
        """
        回复消息, 保证回复消息时统一格式

        Args:
            client: Class: socket 对象
            status: bool: 状态，告诉cilent端发送的消息是否符合协议格式

        Returns:
            NA
        """
        if status == True:
            response = {"status": "recv_ok"}
        else:
            response = {"status": "recv_fail"}
        response = json.dumps(response)
        full_msg = f"{response}mstar"
        client.sendall(full_msg.encode('utf-8'))

    def check_send_status(self):
        """
        检查发送消息是否成功

        Args:
            NA

        Returns:
            result: Ture or False
        """
        try:
            response = self.client.recv(self.rev_max_datalen)
        except socket.timeout:
            logger.print_error("recv timeout!")
            return False
        if isinstance(response, bytes):
             response = response.decode('utf-8')
             response_msg_list = self.parasing_data(response)
        try:
            for item in response_msg_list:
                param = json.loads(item)
                if param['status'] == 'recv_ok':
                    return True
                else:
                    return False
        except Exception as e:
            logger.print_error(f"Exception e:{e}\n")
            return False

    def parasing_data(self, msg):
        """
        解析socket接收到的信息

        Args:
            msg: socket接收到数据

        Returns:
            list: 每个成员是以分隔符区分的字典
        """
        res_msg_list = []
        if isinstance(msg, bytes):
            tmprequest = re.split(self.delimiter, msg.decode('utf-8'))
            # logger.print_info(f"thread_callfun Received no strip: {tmprequest}\n")
            msg = msg.decode('utf-8').strip(self.delimiter)
            res_msg_list = re.split(self.delimiter, msg)
        return res_msg_list

    def close_serial(self, client, msg):
        """
        关闭串口设备

        Args:
            NA

        Returns:
            NA
        """
        self.serial_port.disconnect()

    def read_serial_data_continue(self, client):
        """
        读取串口数据并返回给client端

        Args:
            NA

        Returns:
            NA
        """
        self.serial_port.read_data_running = True
        self.serial_port.read_data_and_send(client)
        client.close()

    def stop_read_serial_data(self, client, msg):
        """
        停止发送串口数据的线程

        Args:
            NA

        Returns:
            NA
        """
        self.serial_port.read_data_running = False
        self.response_msg_to_client(client, True)

    def write_serial(self, client, msg):
        """
        写入命令到串口

        Args:
            NA

        Returns:
            NA
        """
        data_to_write = msg["data"]
        self.serial_port.send_data(data_to_write.encode('utf-8'))
        self.response_msg_to_client(client, True)

    def client_close(self, client, msg):
        """
        cmd client_close对应动作,client退出

        Args:
            msg: socket接收到数据

        Returns:
            NA
        """
        # logger.print_info("client close!!!!")
        self.response_msg_to_client(client, True)
        client.close()
        # 退出thread_callfun线程
        sys.exit()

    def cold_reboot(self, client, msg):
        """
        继电器下电再上电，继电器设备不能长时间占用，使用完毕里面释放
        Args:
            NA
        Returns:
            NA
        """
        rs232_contrl_handle = rs232_contrl(relay=int(relay_port), com=dev_uart)
        logger.print_info("init rs232_contrl_handle, [%s:%s]!\n" \
                                             %(dev_uart, relay_port))
        rs232_contrl_handle.power_off()
        time.sleep(2)
        rs232_contrl_handle.power_on()
        rs232_contrl_handle.close()
        logger.print_info("closed rs232_contrl_handle.")

    def add_case_name_to_uartlog(self, client, msg):
        case_name = msg['case_name']
        self.serial_port.add_case_name_to_uartlog(case_name)
        self.response_msg_to_client(client, True)

    def server_exit(self, client):
        """
        cmd server_exit对应动作,退出server.py主进程

        Args:
            msg: socket接收到数据

        Returns:
            NA
        """
        self.response_msg_to_client(client, True)
        client.close()
        self.server_socket.close()
        self.server_stop()

    def thread_callfun(self, client):
        """
        client端对应子线程，根据接收到的消息处理不同的业务

        Args:
            client: socket

        Returns:
            NA
        """
        request_msg_list = []
        while True:
            request = client.recv(self.rev_max_datalen)
            request_msg_list = self.parasing_data(request)
            for item in request_msg_list:
                param = json.loads(item)
                cmd = param['cmd']
                if hasattr(server_handle, cmd):
                    cmd_callback = getattr(server_handle, cmd)
                    cmd_callback(client, param)
            request_msg_list = []
            time.sleep(0.01)

    def get_client_data(self):
        """
        等待client端连接，接收到连接信息后创建子线程处理

        Args:
            NA

        Returns:
            NA
        """
        while self.server_thread_running:
            # 阻塞等待client端连接
            client, addr = self.server_socket.accept()
            logger.print_info(f"[INFO] Accepted connection from {addr[0]}:{addr[1]}")
            # 每次client的第一条消息特殊处理，判断是否是退出server命令
            request = client.recv(self.rev_max_datalen)
            request_msg_list = self.parasing_data(request)
            for item in request_msg_list:
                # logger.print_info("item" + item)
                param = json.loads(item)
                cmd = param['cmd']
                if cmd == 'server_exit':
                    self.server_exit(client)
                    return 0
                if cmd == 'read_serial_data_continue':
                    self.thread_pool.submit(self.read_serial_data_continue, client)
                    continue
                if hasattr(server_handle, cmd):
                    cmd_callback = getattr(server_handle, cmd)
                    cmd_callback(client, param)
            # 将每个client连接加入到线程池
            self.thread_pool.submit(self.thread_callfun, client)

    def server_start(self):
        logger.print_info("server_start\n")
        # 打开设备列表中的设备
        self.device_init()
        # 绑定 IP 和端口
        self.server_socket.bind((self.host, self.port))
        # 监听连接
        self.server_socket.listen(self.listen_client_num)
        self.server_thread_running = True
        self.server_handler = threading.Thread(target=self.get_client_data)
        self.server_handler.start()
        return 0

    def server_stop(self):
        self.server_thread_running = False
        # 关闭各设备
        self.device_deinit()

if __name__ == "__main__":
    server_handle = server_handle()
    server_handle.server_start()