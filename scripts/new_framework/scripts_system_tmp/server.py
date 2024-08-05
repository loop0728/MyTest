import sys
import time
import socket
import threading
import json
import re
import errno
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
        self.server_run_state_lock = threading.Lock()
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

    def response_msg_to_client(self, client, status, data=''):
        """
        回复消息, 保证回复消息时统一格式

        Args:
            client: Class: socket 对象
            status: bool: 状态，告诉cilent端发送的消息是否符合协议格式

        Returns:
            NA
        """
        if status == True:
            response = {"status": "recv_ok", "data": data}
        else:
            response = {"status": "recv_fail", "data": ""}
        response = json.dumps(response)
        full_msg = f"{response}mstar"
        print(f"response msg: {full_msg}")
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

    def read_serial(self, client, msg):
        print(f'server read_serial')
        ret, data = self.serial_port.read_line()
        self.response_msg_to_client(client, ret, data)

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
        self.serial_port.set_log_prefix(case_name)
        self.response_msg_to_client(client, True)

    def clear_case_name_in_uartlog(self, client, msg):
        self.serial_port.clear_log_prefix()
        self.response_msg_to_client(client, True)

    def get_borad_cur_state(self, client, msg):
        status = self.serial_port.get_bootstage()
        self.response_msg_to_client(client, True, status)

    def clear_borad_cur_state(self, client, msg):
        self.serial_port.clear_bootstage()
        self.response_msg_to_client(client, True)

    def server_exit(self, client, msg):
        """
        cmd server_exit对应动作,退出server.py主进程

        Args:
            msg: socket接收到数据

        Returns:
            NA
        """
        with self.server_run_state_lock:
            self.server_thread_running = False
        logger.print_warning(f"server exit now!!")
        self.response_msg_to_client(client, True)
        self.server_handler.join()
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
            with self.server_run_state_lock:
                run_state = self.server_thread_running
            if run_state == False:
                break
            request = client.recv(self.rev_max_datalen)
            request_msg_list = self.parasing_data(request)
            for item in request_msg_list:
                param = json.loads(item)
                cmd = param['cmd']
                print(f'thread_callfun: {cmd}')
                if hasattr(server_handle, cmd):
                    print(f'cmd_callback, {cmd}, param: {param}')
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
        while True:
            with self.server_run_state_lock:
                run_state = self.server_thread_running
            if run_state == False:
                print(f'shutdown thread pool =================')
                self.thread_pool.shutdown(wait=True)
                break
            # 阻塞等待client端连接
            try:
                client, addr = self.server_socket.accept()
                logger.print_info(f"[INFO] Accepted connection from {addr[0]}:{addr[1]}")
                # 每次client的第一条消息特殊处理，判断是否是退出server命令
                    # request = client.recv(self.rev_max_datalen)
                    # request_msg_list = self.parasing_data(request)
                    # for item in request_msg_list:
                    #     # logger.print_info("item" + item)
                    #     param = json.loads(item)
                    #     cmd = param['cmd']
                    #     print(f"cmd: {cmd}")
                    #     if cmd == 'server_exit':
                    #         self.server_exit(client)
                    #         return 0
                    #     if hasattr(server_handle, cmd):
                    #         cmd_callback = getattr(server_handle, cmd)
                    #         cmd_callback(client, param)
                # 将每个client连接加入到线程池
                self.thread_pool.submit(self.thread_callfun, client)
            except socket.error as e:
                if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                    raise
        #self.server_exit(client)
        print(f'get_client_data stop =====================')

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
        # 关闭各设备
        self.device_deinit()
        print(f'exit server python')
        sys.exit()

if __name__ == "__main__":
    server_handle = server_handle()
    server_handle.server_start()