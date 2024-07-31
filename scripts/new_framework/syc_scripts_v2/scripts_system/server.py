import sys
import os
import time
import socket
import threading
import json
import ast
import re
from PythonScripts.variables import net_connect_port
from pathlib import Path
sys.path.append("PythonScripts")
from logger import logger
from concurrent.futures import ThreadPoolExecutor
from uart_record import create_and_start_uartlog_contrl,stop_and_close_uartlog_contrl
from uartlog_contrl import uartlog_contrl
from rs232_contrl import rs232_contrl
from variables import log_path, uart_port, dev_uart, relay_port
#from PythonScripts.uart_record import create_and_start_uartlog_contrl,stop_and_close_uartlog_contrl

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
        self.server_thread_run    = True
        self.max_workers = max_workers
        self.listen_client_num = listen_client_num
        self.rev_max_datalen = rev_max_datalen
        self.uartlog_contrl_handle = uartlog_contrl(uart_port, log_path)
        self.cur_board_state = 'Unknow'
        self.delimiter = 'mstar'
        # 创建 Socket 对象
        self.thread_pool = ThreadPoolExecutor(self.max_workers)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.server_socket:
           self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def send_data_to_client(self):
        return True

    def set_uartlog_keyword(self, client, respond_msg):
        return True

    def add_case_name_to_uartlog(self, client, respond_msg):
        case_name = respond_msg['case_name']
        self.uartlog_contrl_handle.add_case_name_to_uartlog(case_name)
        respond_msg = json.dumps(respond_msg,cls=MyEncoder,indent=4)
        client.sendall(respond_msg.encode('utf-8'))

    def open_case_uart_bak_file(self, client, respond_msg):
        #logger.print_info(f"open_case_uart_bak_file list num={len(respond_msg)}\n")
        bak_log_path = respond_msg['bak_log_path']
        self.uartlog_contrl_handle.open_case_uart_bak_file(bak_log_path)
        respond_msg['bak_log_path'] = bak_log_path
        respond_msg = json.dumps(respond_msg,cls=MyEncoder,indent=4)
        #logger.print_warning("respond_msg: %s\n" % respond_msg)
        client.sendall(respond_msg.encode('utf-8'))

    def still_send_uartlog_data(self, client, respond_msg):
        last_uartline = ''
        uartline = self.uartlog_contrl_handle.get_searia_buf()
        if isinstance(uartline, bytes):
           uartline = uartline.decode('utf-8')
        if uartline != '' and last_uartline != uartline:
           last_uartline = uartline
           #logger.print_warning("loop thread_callfun respond_msg %s\n" %(respond_msg))
           respond_msg['uartlog_curline'] = uartline
           #logger.print_warning("loop thread_callfun respond_msg %s\n" %(respond_msg))
           respond_msg = json.dumps(respond_msg,cls=MyEncoder,indent=4)
           if isinstance(respond_msg, bytes):
              respond_msg = respond_msg.decode('utf-8')
           client.sendall(respond_msg)

    def get_borad_uartlogline(self, client, respond_msg):
        uartline = self.uartlog_contrl_handle.get_searia_buf()
        last_uartline = ''
        if isinstance(uartline, bytes):
            uartline = uartline.decode('utf-8')
        if uartline != '' and last_uartline != uartline and self.uartlog_contrl_handle.in_waiting():
            last_uartline = uartline
        respond_msg['uartlog_curline'] = uartline
        respond_msg = json.dumps(respond_msg,cls=MyEncoder,indent=4)
        #logger.print_info(f"thread_callfun cur_uartline: {uartline} msg:{respond_msg}\n")
        client.sendall(respond_msg.encode('utf-8'))
        #logger.print_info(f"thread_callfun cur_uartline: {uartline} msg:{respond_msg}\n")

    def get_borad_cur_state(self, client, respond_msg):
        #self.uartlog_contrl_handle.send_command("\n")
        cur_board_state = self.uartlog_contrl_handle.get_borad_cur_state()
        #logger.print_info("cur_board_state: %s\n" % cur_board_state)
        respond_msg['board_sta'] = cur_board_state
        respond_msg = json.dumps(respond_msg,cls=MyEncoder,indent=4)
        client.sendall(respond_msg.encode('utf-8'))
        #logger.print_info("respond_msg: %s\n" % respond_msg)

    def clear_borad_cur_state(self, client, respond_msg):
        cur_board_state = self.uartlog_contrl_handle.clear_borad_cur_state()
        #logger.print_info("cur_board_state: %s\n" % cur_board_state)
        respond_msg['board_sta'] = cur_board_state
        respond_msg = json.dumps(respond_msg,cls=MyEncoder,indent=4)
        #logger.print_info("respond_msg: %s\n" % respond_msg)
        client.sendall(respond_msg.encode('utf-8'))

    def uboot_reset(self, client, respond_msg):
        self.uartlog_contrl_handle.send_command("reset\n")

    def client_close(self, client, respond_msg):
        respond_msg['client_dis'] = 'client_dis'
        respond_msg = json.dumps(respond_msg,cls=MyEncoder,indent=4)
        #logger.print_info("client_close:respond_msg: %s\n" % respond_msg)
        client.sendall(respond_msg.encode('utf-8'))
        client.close()

    def set_check_uartlog_keyword_list(self, client, respond_msg):
        #logger.print_info("set_check_uartlog_keyword_list: %s\n" % respond_msg)
        if 'check_uart_keyword_list' in respond_msg:
           check_uart_keyword_list = respond_msg['check_uart_keyword_list']
           check_uart_keyword_list = ast.literal_eval(check_uart_keyword_list)
           self.uartlog_contrl_handle.set_check_keyword_list(check_uart_keyword_list)
        else:
           respond_msg['state'] = 'recv_fail'
        respond_msg = json.dumps(respond_msg,cls=MyEncoder,indent=4)
        #logger.print_info("respond_msg: %s\n" % respond_msg)
        client.sendall(respond_msg.encode('utf-8'))

    def get_check_uartlog_keyword_dict(self, client, respond_msg):
        respond_msg['keyword_cnt_dict'] = self.uartlog_contrl_handle.get_case_have_keyword_dicts()
        logger.print_info("respond_msg: %s\n" % respond_msg)
        respond_msg = json.dumps(respond_msg,cls=MyEncoder,indent=4)
        client.sendall(respond_msg.encode('utf-8'))

    def thread_callfun(self, request_msg_list, client):
        last_uartline = ''
        while True:
            if len(request_msg_list) == 0:
               #logger.print_info("go thread_callfun=client.recv====!\n")
               request = client.recv(self.rev_max_datalen)
               if isinstance(request, bytes):
                   tmprequest = re.split(self.delimiter, request.decode('utf-8'))
                   #logger.print_info(f"thread_callfun Received no strip: {tmprequest}\n")
                   request = request.decode('utf-8').strip(self.delimiter)
                   request_msg_list = re.split(self.delimiter, request)
                   #logger.print_info(f"Received: {request_msg_list} list num={len(request_msg_list)}\n")
            if len(request_msg_list) > 0:
                for index in range(0, len(request_msg_list)):
                    param = json.loads(request_msg_list[index])
                    #print("param: %s" %param)
                    case_name = param['case_name']
                    cmd = param['cmd']
                    #print("case_name:%s cmd:%s\n" %(case_name,cmd))
                    respond_msg = param
                    respond_msg['state'] = 'recv_ok'
                    if cmd !='NULL' and cmd != '' and hasattr(server_handle, cmd):
                       cmd_callback = getattr(server_handle, cmd)
                       cmd_callback(client, respond_msg)
                       if cmd == 'client_close':
                            return 0
                       cmd = 'NULL'
                    else:
                       if cmd == 'NULL':
                          continue
                       ret_buf = ''
                       ret_match_buffer = ''
                       run_sta = 'run_fail'
                       run_cmd_timeout = int(param['timeout'])
                       rev_cmdlen = int(param['cmdlen'])
                       #logger.print_info("john case_name:%s cmd:%s cur_len_size:%s rev_cmdlen:%s\n" %(case_name,cmd,len(cmd),rev_cmdlen))
                       if rev_cmdlen == len(cmd):
                           if run_cmd_timeout == 0:
                              ret_buf,wlen = self.uartlog_contrl_handle.send_command(cmd)
                              #logger.print_info("ret_buf case_name:%s cmd:%s cur_len_size:%s rev_cmdlen:%s\n" %(case_name,cmd,len(cmd),rev_cmdlen))
                              if wlen >= len(cmd):
                                 run_sta = 'run_ok'
                           else:
                               wait_keyword = param['wait_keyword']
                               check_keyword = param['check_keyword']
                               self.uartlog_contrl_handle.clear_check_keyword_and_send_cmd()
                               self.uartlog_contrl_handle.set_check_keyword_and_send_cmd(wait_keyword, cmd, check_keyword)
                               if self.uartlog_contrl_handle.in_waiting() == False:
                                  self.uartlog_contrl_handle.send_command('')

                               is_run,check_key,ret_match_buffer = self.uartlog_contrl_handle.cmd_run_stat()
                               if isinstance(ret_match_buffer, bytes):
                                   ret_match_buffer = ret_match_buffer.decode('utf-8')
                               #logger.print_info("start is_run:%s, check_key:%s ret_match_buffer:%s\n" %(is_run,check_key,ret_match_buffer))
                               try_time = 0
                               while True:
                                  if check_key == '' and is_run:
                                      run_sta = 'run_ok'
                                      #logger.print_info("is_run:%s, check_key:%s ret_match_buffer:%s run_cmd_timeout:%s\n" %(is_run,check_key,ret_match_buffer,run_cmd_timeout))
                                      break
                                  is_run,check_key,ret_match_buffer = self.uartlog_contrl_handle.cmd_run_stat()
                                  if isinstance(ret_match_buffer, bytes):
                                     ret_match_buffer = ret_match_buffer.decode('utf-8')
                                  try_time = try_time + 1
                                  time.sleep(0.001)
                                  if try_time > run_cmd_timeout*1000:
                                    logger.print_error("case_name run_cmd_timeout\n")
                                    ret_buf = self.uartlog_contrl_handle.get_searia_buf()
                                    if isinstance(ret_buf, bytes):
                                       ret_buf = ret_buf.decode('utf-8')
                                    if ret_buf != '' and check_key in ret_buf:
                                       ret_match_buffer = ret_buf
                                       run_sta = 'run_ok'
                                    logger.print_error("is_run:%s, check_key:%s ret_match_buffer:%s\n" %(is_run,check_key,ret_match_buffer))
                                    break

                               if try_time <= run_cmd_timeout:
                                    run_sta = 'run_ok'
                                    ret_buf = self.uartlog_contrl_handle.get_searia_buf()
                               if not is_run:
                                    run_sta = 'cmd_no_run'
                       else:
                           respond_msg['state'] = 'recv_fail'
                       if isinstance(ret_buf, bytes):
                           ret_buf = ret_buf.decode('utf-8')
                       respond_msg['cmd_exc_sta'] = run_sta
                       respond_msg['ret_buf'] = ret_buf
                       respond_msg['ret_match_buffer'] = ret_match_buffer
                       respond_msg = json.dumps(respond_msg,cls=MyEncoder,indent=4)
                       if run_sta == 'run_fail':
                          logger.print_warning("other_cmd:respond_msg: %s\n" %respond_msg)
                       elif run_sta == 'cmd_no_run':
                          logger.print_error("other_cmd:respond_msg: %s\n" %respond_msg)
                       client.sendall(respond_msg.encode('utf-8'))
                       self.uartlog_contrl_handle.clear_check_keyword_and_send_cmd()
                       respond_msg = []
                       time.sleep(1)
                       cmd = 'NULL'

                request_msg_list = []
                time.sleep(0.01)

    def get_client_data(self):
        request_msg_list = []
        while self.server_thread_run:
            client,addr = self.server_socket.accept()
            logger.print_info(f"[INFO] Accepted connection from {addr[0]}:{addr[1]}")
            request = client.recv(self.rev_max_datalen)
            if isinstance(request, bytes):
                tmprequest = re.split(self.delimiter, request.decode('utf-8') )
                logger.print_info(f"Received no strip: {tmprequest}\n")
                request = request.decode('utf-8').strip(self.delimiter)
                request_msg_list = re.split(self.delimiter, request)
                if request_msg_list[0] == '' and len(request_msg_list) == 1:
                    continue
            #logger.print_info(f"Received: {request_msg_list} list num={len(request_msg_list)}\n")
            for index in range(0, len(request_msg_list)):
                #logger.print_info("request_msg_list type: %s" %type(request_msg_list[index]))
                param = json.loads(request_msg_list[index])
                case_name = param['case_name']
                if case_name == 'server_exit':
                    respond_msg = param
                    respond_msg['state'] = 'recv_ok'
                    respond_msg['server_exit'] = 'server_exit'
                    respond_msg = json.dumps(respond_msg,cls=MyEncoder,indent=4)
                    logger.print_warning("server_exit:respond_msg: %s\n" % respond_msg)
                    client.sendall(respond_msg.encode('utf-8'))
                    client.close()
                    self.server_socket.close()
                    self.server_stop()
                    return 0
            if len(request_msg_list):
               self.thread_pool.submit(self.thread_callfun, request_msg_list, client)
            time.sleep(0.0001)

    def server_start(self):
        logger.print_info("server_start\n")
        # 绑定 IP 和端口
        self.server_socket.bind(('localhost', int(net_connect_port)))
        # 监听连接
        self.server_socket.listen(self.listen_client_num)
        self.thread_run = True
        self.uartlog_contrl_handle.start_record()
        self.server_handler = threading.Thread(target=self.get_client_data)
        self.server_handler.start()
        return 0

    def server_stop(self, timeout=0):
        self.server_thread_run = False
        self.uartlog_contrl_handle.stop_record()
        self.uartlog_contrl_handle.close()
      #  self.server_handler.join(timeout)


if __name__ == "__main__":
     server_handle = server_handle()
     server_handle.server_start()


