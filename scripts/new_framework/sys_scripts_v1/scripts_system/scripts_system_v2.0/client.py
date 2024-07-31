import sys
import socket
import time
import threading
import json
import numpy as np

from PythonScripts.variables import net_connect_port
from pathlib import Path
sys.path.append("PythonScripts")

from rs232_contrl import rs232_contrl
from variables import dev_uart, relay_port, log_path
from logger import logger

class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, bytes):
            return str(obj, encoding='utf-8');
        return json.JSONEncoder.default(self, obj)


class client_handle():

    def __init__(self, case_name='', protocol='uart', rev_max_datalen=4096):
       self.case_name = case_name
       self.msg = ''
       self.rev_max_datalen = rev_max_datalen
       self.cur_server_data = ''
       self.cur_telnet_data = ''
       self.threadLock = threading.Lock()  # 多线程锁
       try_time = 0
       self.ret = -1
       self.protocol = protocol
       self.delimiter = 'mstar'
       self.borad_cur_state = ''
       self.borad_cur_line = ''
       super().__init__()
       try:
          self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
          self.client.connect(('localhost',int(net_connect_port)))
       except Exception as e:
           logger.print_warning('maybe sever is offline:error[%s]' %e)
           time.sleep(1)
           try_time += 1
           if try_time > 100:
               raise

    def client_handle_close(self):
        client_handle.close()

    def cold_reboot(self):
       # 创建和启动 rs232_contrl_handle
        rs232_contrl_handle = rs232_contrl(relay=int(relay_port), com=dev_uart)
        logger.print_info("init rs232_contrl_handle, [%s:%s]!\n" \
                                             %(dev_uart,relay_port))
        rs232_contrl_handle.power_off()
        time.sleep(2)
        rs232_contrl_handle.power_on()
        rs232_contrl_handle.close()
        logger.print_info("closed rs232_contrl_handle.")

    def client_send_cmd(self, msg, is_wait_reponse = True):
       state = False
       param = []
       try:
          self.client.sendall(msg.encode('utf-8'))
       except Exception as e:
          logger.print_warning(f"Exception e:{e}\n")
          return 255, param
       if is_wait_reponse:
          response = self.client.recv(self.rev_max_datalen)
          if isinstance(response, bytes):
             response = response.decode('utf-8')
          #logger.print_info(type(response))
          #logger.print_info(response)
          try:
             param = json.loads(response)
             #logger.print_info(type(param))
             #logger.print_info(param)
             if param['state'] == "recv_ok":
                state = True
          except Exception as e:
             logger.print_error(f"Exception e:{e}\n")
       if param != '' and param != '[]' and 'state' in param and param['state'] != 'recv_ok':
          logger.print_error("open_case_uart_bak_file response :%s\n" % param)
       return (state,param)

    def client_get_server_data(self):
        response = self.client.recv(self.rev_max_datalen)
        if isinstance(response, bytes):
           response = response.decode('utf-8')
           param = json.loads(response)
           if param['state'] == "recv_ok":
              state = True
        return param

    def still_send_uartlog_data(self, is_wait_response = True):
        msg = '{' + '"case_name":"{}","cmd":"still_send_uartlog_data"'.format(self.case_name) + '}' + self.delimiter
        ret,self.response = self.client_send_cmd(msg, is_wait_response)
        return (ret,self.response)

    def open_case_uart_bak_file(self, case_name_uart_log, is_wait_response = True):
        msg = '{' + '"case_name":"{}","cmd":"open_case_uart_bak_file","bak_log_path":"{}"'.format(self.case_name,case_name_uart_log) + '}' + self.delimiter
        ret,self.response = self.client_send_cmd(msg, is_wait_response)
        if self.response != '' and self.response != '[]' and 'state' in self.response and self.response['state'] != 'recv_ok':
           logger.print_error("open_case_uart_bak_file response :%s\n" % self.response)
        logger.print_info("open_case_uart_bak_file response :%s\n" % self.response)
        return (ret,self.response)

    def still_send_telnet_data(self, is_wait_response = False):
        msg = '{' + '"case_name":"{}","cmd":"still_send_telnet_data"'.format(self.case_name) + '}' + self.delimiter
        ret,self.response = self.client_send_cmd(msg, is_wait_response)
        return (ret,self.response)

    def uboot_reset_reboot(self, is_wait_response = True):
        msg = '{' + '"case_name":"{}","cmd":"uboot_reset"'.format(self.case_name) + '}' + self.delimiter
        ret,self.response = self.client_send_cmd(msg, is_wait_response)
        return (ret,self.response)

    def kernel_reboot(self, is_wait_response = True):
        msg = '{' + '"case_name":"{}","cmd":"kernel_reset"'.format(self.case_name) + '}' + self.delimiter
        ret,self.response = self.client_send_cmd(msg, is_wait_response)
        return (ret,self.response)

    def get_borad_cur_state(self, is_wait_response = True):
        msg = '{' + '"case_name":"{}","cmd":"get_borad_cur_state"'.format(self.case_name) + '}' + self.delimiter
        ret,self.response = self.client_send_cmd(msg, is_wait_response)
        if self.response != '' and self.response != '[]' and 'board_sta' in self.response:
           self.borad_cur_state = self.response['board_sta']
        return self.borad_cur_state

    def clear_borad_cur_state(self, is_wait_response = True):
        msg = '{' + '"case_name":"{}","cmd":"clear_borad_cur_state"'.format(self.case_name) + '}' + self.delimiter
        ret,self.response = self.client_send_cmd(msg, is_wait_response)
        #logger.print_info("clear_borad_cur_state response :%s\n" % self.response)
        if self.response != '' and self.response != '[]' and 'board_sta' in self.response:
           self.borad_cur_state = self.response['board_sta']
        return self.borad_cur_state

    def get_borad_uartlogline(self, is_wait_response = True):
        msg = '{' + '"case_name":"{}","cmd":"get_borad_uartlogline"'.format(self.case_name) + '}' + self.delimiter
        ret,self.response = self.client_send_cmd(msg, is_wait_response)
        #logger.print_info("get_borad_uartlogline response :%s\n" % self.response)
        if self.response != '' and self.response != '[]' and 'uartlog_curline' in self.response:
           self.borad_cur_line = self.response['uartlog_curline']
        return self.borad_cur_line

    def client_send_cmd_to_server(self, cmd = '', is_wait_response = True, wait_keyword='',check_keyword='', timeout=0):
        cmd_exc_sta = 'run fail'
        ret_buf = ''
        ret_match_buffer = ''
        if wait_keyword == '' and check_keyword == '':
           msg = '{' + '"case_name":"{}","cmd":"{}","cmdlen":"{}","timeout":"{}"'.format(self.case_name, cmd,len(cmd), timeout) + '}' + self.delimiter
        else:
           msg = '{' + '"case_name":"{}","cmd":"{}","cmdlen":"{}","timeout":"{}","wait_keyword":"{}","check_keyword":"{}"'.format(self.case_name,\
                                                                        cmd, len(cmd), timeout, wait_keyword,check_keyword) + '}' + self.delimiter
        #logger.print_info(f"send msg:{msg}\n")
        ret,self.response = self.client_send_cmd(msg, is_wait_response)

        if self.response != '' and self.response != '[]' and 'cmd_exc_sta' in self.response:
           cmd_exc_sta = self.response['cmd_exc_sta']
        if self.response != '' and self.response != '[]' and 'ret_buf' in self.response:
           ret_buf = self.response['ret_buf']
        if self.response != '' and self.response != '[]' and 'ret_match_buffer' in self.response:
           ret_match_buffer = self.response['ret_match_buffer']

        if self.response != '' and self.response != '[]' and 'state' in self.response and self.response['state'] != 'recv_ok':
           logger.error("client_send_cmd_to_server response :%s\n" % self.response)

        return (cmd_exc_sta, ret_buf, ret_match_buffer)

    def add_case_name_to_uartlog(self, case_name='', is_wait_response = True):
        if case_name == '':
           msg = '{' + '"case_name":"{}","cmd":"add_case_name_to_uartlog"'.format(self.case_name) + '}' + self.delimiter
        else:
           msg = '{' + '"case_name":"{}","cmd":"add_case_name_to_uartlog"'.format(case_name) + '}' + self.delimiter
        ret,self.response = self.client_send_cmd(msg, is_wait_response)
        #logger.print_info("add_case_name_to_uartlog response :%s\n" % self.response)

    def client_set_check_uartlog_keyword_arr(self, cmd = '', set_check_keyword=[], is_wait_response = True, timeout=0):
        msg = '{' + '"case_name":"{}","cmd":"set_check_uartlog_keyword_list", "check_uart_keyword_list":"{}"'.format(self.case_name,set_check_keyword) + '}' + self.delimiter
        logger.print_info("client_set_check_uartlog_keyword_arr msg :%s\n" % msg)
        ret,self.response = self.client_send_cmd(msg, is_wait_response)
        return ret,self.response

    def client_get_check_uartlog_keyword_dict(self, cmd = '', set_check_keyword=[], is_wait_response = True, timeout=0):
        msg = '{' + '"case_name":"{}","cmd":"get_check_uartlog_keyword_dict", "check_uart_keyword_list":"{}"'.format(self.case_name,set_check_keyword) + '}' + self.delimiter
        logger.print_info("client_get_check_uartlog_keyword_dict msg :%s\n" % msg)
        ret,self.response = self.client_send_cmd(msg, is_wait_response)
        uart_keyword_dict = {}
        if self.response != '' and self.response != '[]' and 'keyword_cnt_dict' in self.response:
           uart_keyword_dict = self.response['keyword_cnt_dict']
        return ret,uart_keyword_dict

    def client_close(self):
        msg = '{' + '"case_name":"{}","cmd":"client_close"'.format(self.case_name) + '}' + self.delimiter
        ret,self.response = self.client_send_cmd(msg)
        #logger.print_info(self.response)
        ret = False
        client_sta = self.response['client_dis']
        if client_sta == 'client_dis':
          ret = True
        return ret

    def server_exit(self):
        msg = '{' + '"case_name":"{}","cmd":"server_exit"'.format(self.case_name) + '}' + self.delimiter
        ret,self.response = self.client_send_cmd(msg)
        if ret != 255:
           logger.info(self.response)
        else:
           return 0
        ret = False
        client_sta = self.response['state']
        if client_sta == 'recv_ok':
          ret = True
        return ret

    def get_uartlog_curline(self):
        return self.cur_server_data

    def get_telnetlog_curline(self):
        return self.cur_telnet_data



def system_case_run(param_list, client_handle):
    module_path_name = param_list[0]
    #logger.print_info("test:param_list[1:]: ", module_path_name)
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

def system_case_run_stress_case_api(argv):
    logger.print_warning(f"system_case_run_stress_case_api !\n")
    case_report_path = ''
    param_list = []
    case_run_cnt = 1
    if len(argv) < 2:
        logger.print_error("system_case_run_api param num less 2\n")
        return 255
    for i in range(1, len(argv)):
        logger.print_info("argv[%s]: %s" %(i, argv[i]))
        if i == 1:
           module_path_name = argv[1]
           param_list.append(module_path_name)
           if module_path_name == 'server_exit':
              client = client_handle(case_name=module_path_name)
              client.ret = client.server_exit()
              return client.ret
        elif i == 2:
           case_name = argv[2]
           param_list.append(case_name)
        else:
           param_list.append(argv[i])
    if len(argv) == 3:
       param_list.append(case_run_cnt)
    param_list.append(log_path)
    logger.print_info(f"case_name:{case_name} module_path_name:{module_path_name} param_list:{param_list}\n")
    client = client_handle(case_name)
    client.ret = system_case_run(param_list, client)
    return client.ret

def system_case_run_case_api(argv):
    logger.print_warning(f"system_case_run_general_case_api !\n")
    case_report_path = ''
    param_list = []
    case_run_cnt = 1
    if len(argv) < 2:
        logger.print_error("system_case_run_api param num less 2\n")
        return 255
    for i in range(1, len(argv)):
        logger.print_info("argv[%s]: %s" %(i, argv[i]))
        if i == 1:
           module_path_name = argv[1]
           param_list.append(module_path_name)
           if module_path_name == 'server_exit':
              client = client_handle(case_name=module_path_name)
              client.ret = client.server_exit()
              return client.ret
        elif i == 2:
           case_name = argv[2]
           param_list.append(case_name)
        else:
           param_list.append(argv[i])
    if len(argv) == 3:
       param_list.append(case_run_cnt)
    param_list.append(log_path)
    client = client_handle(case_name)
    client.ret = system_case_run(param_list, client)
    return client.ret

def system_case_run_api(argv):
    case_report_path = ''
    param_list = []
    module_path_name = ''
    case_name = ''
    case_run_cnt = 1
    if len(argv) < 2:
       logger.print_error("system_case_run_api param num less 2\n")
       return 255
    if len(argv) > 2:
       logger.print_warning(f"1:{argv[1]} 2:{argv[2]}\n")
    ret = system_case_run_case_api(argv)
    return ret
    '''if module_path_name != 'AOV/stress_case/':
    system_case_run_general_case_api(argv)
    else:
        system_case_run_stress_case_api(argv)'''

if __name__ == "__main__":
    ret = system_case_run_api(sys.argv)
    sys.exit(ret)
