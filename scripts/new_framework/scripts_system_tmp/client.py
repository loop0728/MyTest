import sys
import socket
import time
import threading
import json
import re

from PythonScripts.variables import net_connect_port, log_path
from PythonScripts.logger import logger

class client_handle():
    def __init__(self, case_name='', protocol='uart', rev_max_datalen=4096):
        self.case_name = case_name
        self.rev_max_datalen = rev_max_datalen
        self.protocol = protocol
        self.delimiter = 'mstar'
        self.read_serial_data_thread = None              # 读serial数据的线程
        self.serial_data_buffer = []                     # server端返回的所有串口数据，user请勿修改
        self.serial_data_tmp = []                        # server端返回的串口数据，user可自行根据需要修改
        self.write_flag = 0                              # 写数据时buffer的位置
        self.read_line_flag = 0                          # 读取数据的位置
        self.data_changed = threading.Event()            # 数据更新事件
        self.serial_data_lock = threading.Lock()
        self.host = 'localhost'
        self.port = int(net_connect_port)
        # 连接到server端

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        for try_time in range(100):
            try:
                self.client_socket.connect((self.host, self.port))
                logger.print_info(f'Connect to {self.host} on {self.port}')
                break
            except socket.timeout:
                logger.print_warning(f'Connection attempt {try_time + 1} time out, retrying ...')
            except socket.error as e:
                logger.print_warning(f'Connection attempt {try_time + 1} failed with error:{e}')
            finally:
                if try_time < 100 - 1:
                    time.sleep(1)

    def _send_msg_to_server(self, msg):
        """
        发送消息, 保证发送消息时统一格式

        Args:
            msg: dict: 发送的消息内容

        Returns:
            NA
        """
        result = False
        msg = json.dumps(msg)
        full_msg = f"{msg}mstar"
        try:
            self.client_socket.sendall(full_msg.encode('utf-8'))
            result = True
        except socket.error as e:
            print(f"An error occurred: {e}")
        return result

    def _parasing_data(self, msg):
        """
        解析socket接收到的信息

        Args:
            msg: socket接收到数据

        Returns:
            list: 每个成员是以分隔符区分的字典
        """
        res_msg_list = []
        #if isinstance(msg, bytes):
        tmprequest = re.split(self.delimiter, msg)
        # logger.print_info(f"thread_callfun Received no strip: {tmprequest}\n")
        msg = msg.strip(self.delimiter)
        print(f'parsing msg: {msg}')
        res_msg_list = re.split(self.delimiter, msg)
        return res_msg_list

    def _send_to_server_and_check_response(self, msg):
        """
        发送命令，并检测发送是否成功

        Args:
            msg: socket接收到数据

        Returns:
            result: Bool True or False
        """
        result = False
        data = ''
        old_timeout = self.client_socket.gettimeout()
        self.client_socket.settimeout(5)       # 设置5秒超时
        try:
            self._send_msg_to_server(msg)
            print(f"_send_msg_to_server done, {msg}")
            response = self.client_socket.recv(self.rev_max_datalen)
            print(f"response:{response}")
            if isinstance(response, bytes):
                response = response.decode('utf-8')
                response_msg_list = self._parasing_data(response)
                for item in response_msg_list:
                    param = json.loads(item)
                    print(f'param: {param}')
                    if param['status'] == 'recv_ok':
                        result = True
                    else:
                        result = False
                    if 'data' in param.keys():
                        data = param['data']
                    else:
                        print(f"data is not in param")
                print(f'data is {data}')
        except Exception as e:
            logger.print_warning(f"Exception e:{e}\n")
            self.client_socket.settimeout(old_timeout)
            return False, data
        self.client_socket.settimeout(old_timeout)
        return result, data

    def write(self, data, des='uart'):
        """
        写数据

        Args:
            data: 写入的数据
            des:写入的目标设备

        Returns:
            result: bool True or False
        """
        #self.write_flag = len(self.serial_data_buffer) + 1
        msg = {"case_name": self.case_name, "cmd": "write_serial", "data": data}
        result,_ = self._send_to_server_and_check_response(msg)
        return result

    def read(self, src='uart'):
        """
        读取一行数据

        Args:
            src: 数据来源

        Returns:
            data: 前一次写命令之后返回结果中的一行数据
        """
        #data = self.serial_data_buffer[self.write_flag:]
        print(f'client read==============================')
        msg = {"case_name": self.case_name, "cmd": "read_serial"}
        result,data = self._send_to_server_and_check_response(msg)
        return result,data

    def add_case_name_to_uartlog(self, case_name=''):
        logger.print_info("client add case name to log file!")
        if case_name == '':
           msg = {"case_name": self.case_name,"cmd": "add_case_name_to_uartlog"}
        else:
           msg = {"case_name": case_name, "cmd": "add_case_name_to_uartlog"}
        result,_ = self._send_to_server_and_check_response(msg)
        return result

    def clear_case_name_in_uartlog(self):
        logger.print_info("client clear case name in log file!")
        msg = {"case_name": self.case_name,"cmd": "clear_case_name_in_uartlog"}
        result,_ = self._send_to_server_and_check_response(msg)
        return result

    def get_borad_cur_state(self):
        logger.print_info("client get board current state")
        msg = {"case_name": self.case_name,"cmd": "get_borad_cur_state"}
        result,status = self._send_to_server_and_check_response(msg)
        print(f'status: {status}')
        return result,status

    def clear_borad_cur_state(self, is_wait_response = True):
        logger.print_info("client clear board current state")
        msg = {"case_name":self.case_name, "cmd":"clear_borad_cur_state"}
        result,_ = self._send_to_server_and_check_response(msg)
        return result

    def close_client(self):
        """
        通知server端client端已关闭, 关闭socket

        Args:
            NA

        Returns:
            result: bool: True or False
        """
        msg = {"case_name": self.case_name,"cmd": "client_close"}
        #result = self._send_msg_to_server(msg)
        result,_ = self._send_to_server_and_check_response(msg)
        self.client_socket.close()
        return result

    def server_exit(self):
        """
        通知server端退出server.py

        Args:
            NA

        Returns:
            result: bool: True or False
        """
        logger.print_info("client send server_exit!")
        msg = {"case_name": self.case_name,"cmd": "server_exit"}
        #result = self._send_msg_to_server(msg)
        result,_ = self._send_to_server_and_check_response(msg)
        print(f'clinet recv server_exit respond')
        self.client_socket.close()
        return result

    def match_keyword_return(self, keyword, wait_timeout = 5):
        """
        获取关键字所在的行

        Args:
            keyword: 需要匹配的关键
            wait_timeout: 等待数据更新超时时间

        Returns:
            result,data: 匹配到关键字后立即返回结果和data
        """
        while True:
            result,line = self.read()
            if result == True:
                if isinstance(line, bytes):
                    line = line.decode('utf-8').strip()
                    if keyword in line:
                        return True, line
            else:
                return  False, ''

def system_case_run(param_list, client_handle):
    module_path_name = param_list[0]
    # logger.print_info("test:param_list[1:]: ", module_path_name)
    module_path = "/".join(module_path_name.split("/")[:-1])
    module_name = module_path_name.split("/")[-1].split(".")[0]

    sys.path.append(module_path)
    module = __import__(module_name)
    logger.print_info("param_list[1:]:", param_list[1:])
    if param_list[1] == "help":
         module.system_help(param_list[1:])
         return 0

    result = module.system_runcase(param_list[1:], client_handle)
    return result

def system_case_run_case_api(argv, case_run_cnt, case_name):
    logger.print_warning(f"system_case_run_general_case_api !\n")
    param_list = []
    param_list.append(argv[1])
    param_list.append(argv[2])
    param_list.append(case_run_cnt)
    param_list.append(case_name)
    param_list.append(log_path)
    client = client_handle(case_name)
    for cnt in range(0, int(case_run_cnt)):
        ret = system_case_run(param_list, client)
        if ret == 0:
            ret_str = '[success][cnt={}][maxcnt={}]'.format(cnt+1, case_run_cnt)
            logger.print_info("[AUTO_TEST][%s][%s][ret:%s]:" %(case_name, ret_str, ret))
        else:
            ret_str = '[Fail][cnt={}][maxcnt={}]'.format(cnt+1, case_run_cnt)
            logger.print_info("[AUTO_TEST][%s][%s][ret:%s]:" %(case_name, ret_str, ret))
    client.close_client()
    return ret

def get_run_case_cnt(input_case_name):
    """
    根据case name判断case需要执行的次数

    Args:
        case_name: case name

    Returns:
        int:
        case_run_cnt
        str:
        output_case_name
    """
    case_run_cnt = 0
    if input_case_name[len(input_case_name)-1:].isdigit() and '_stress_' in input_case_name:
        parase_list = input_case_name.split('_stress_')
        if len(parase_list) != 2:
            return case_run_cnt,input_case_name
        case_run_cnt = int(parase_list[1])
        output_case_name = parase_list[0]
        logger.print_info(f"case_run_cnt: {case_run_cnt} case_name:{output_case_name}\n")
    else:
        case_run_cnt = 1
        output_case_name = input_case_name
    return case_run_cnt,output_case_name

def system_case_run_api(argv):
    """
    client端总入口

    Args:
        argv[0]: client.py
        argv[1]: scripts          eg: AOV/ttff_ttcl/ttff_ttcl.py
        argv[2]: case_name        eg: ttff_ttcl

    Returns:
        int:
        result: 0:pass other:fail
    """
    if len(argv) < 2:
        logger.print_error("system_case_run_api param num less 2\n")
        return 255
    if argv[1] == 'server_exit':
        client = client_handle(case_name='server_exit')
        client.ret = client.server_exit()
        return client.ret
    if len(argv) > 2:
        logger.print_warning(f"1:{argv[1]} 2:{argv[2]}\n")
        input_case_name = argv[2]
        case_run_cnt, case_name = get_run_case_cnt(input_case_name)
        result = system_case_run_case_api(argv, case_run_cnt, case_name)
        return result

if __name__ == "__main__":
    ret = system_case_run_api(sys.argv)
    sys.exit(ret)