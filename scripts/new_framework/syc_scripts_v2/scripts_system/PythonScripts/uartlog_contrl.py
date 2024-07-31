#__all__ = ['_uartlog_contrl']

import sys
import threading
import serial
import time
import os
import platform
import json
from logger import logger

def logPrinter(mesg='Nothing to log.', log_obs=1):
    if log_obs:
        mesg = time.strftime('[%Y.%m.%d %H:%M:%S] ', time.localtime(time.time())) + str(mesg)
        logger.print_warning(mesg)


class uartlog_contrl():
    '''
        串口控制类 ，执行串口命令，并且通过多线程记录串口log
    '''

    def __init__(self, port='COM4', logfile='', baudrate=115200, log_obs=1):
        self.ignore = False  # 是否忽略串口log的检测
        self.log_obs = log_obs
        self.os_info = platform.system()
        port_info = port
        if self.os_info == 'Windows':
           port_info = 'COM' + port
        self.port = port_info
        self.keyword_dicts = {}
        self.keyword_list = []
        self.logfile = logfile
        self.baudrate = baudrate
        self.timeout = 5
        self.hold_env = False
        self.hold_flag = False
        self.quick_return = False
        self.uart_line = ''
        self.uart_line_output = ''
        self.have_keyword_dicts = {}
        self.check_keyword = ''
        self.cmd = ''
        self.send_time = 0
        self.is_run_cmd = False
        self.is_rw_wdeta = False
        self.add_prefix_buf = ''
        self.is_add_allline = False
        self.case_uart_bak_file = ''
        self.isline_update = False
        self.board_state = 'Unknow'
        self.wait_keyword = ''
        self.ret_match_buffer = ''
        self.board_state_in_boot_str = 'SigmaStar #'
        self.board_state_in_kernel_str = '/ #'

        self.threadLock = threading.Lock()  # 多线程锁
        super().__init__()

    def mkdir_path(self, path):
        if path == '':
           return
        if self.os_info == 'Windows':
           os.mkdir(path)
        else:
           os.makedirs(path)

    def get_borad_cur_state(self) -> str:
         return self.board_state

    def clear_borad_cur_state(self) -> str:
         self.board_state = 'Unknow'
         return self.board_state

    @logger.print_line_info
    def start_record(self):
        if self.logfile == '':
            self.logfile = './log/%s_%s.log' % (time.strftime('%Y%m%d_%H%M%S', time.localtime(time.time())), self.port)
        self.crashlogFile = self.logfile.replace('.log', '') + '_crash.log'  # 串口log异常文件名
        logPrinter(mesg='Create Log File "%s"' % self.logfile, log_obs=self.log_obs)
        self.console = serial.Serial(port=self.port, baudrate=self.baudrate, timeout=self.timeout)
        self.console.read_buffer_size = 4096
        self.console.write_buffer_size = 4096
        self.serRunning = True
        self.uart_line = ''
        # 守护线程，记录串口log
        if self.logfile == '':
            self.logfile = './log/%s_%s.log' % (time.strftime('%Y%m%d_%H%M%S', time.localtime(time.time())), self.port)
        # dir_path = self.logfile[:self.logfile.rfind('/')]
        dir_path = os.path.dirname(self.logfile)
        if not os.path.exists(dir_path):
            self.mkdir_path(dir_path)
        self.crashlogFile = self.logfile.replace('.log', '') + '_crash.log'  # 串口log异常文件名
        #with open(self.logfile, 'a+') as f:
        try:
           self.logfile_fd = open(self.logfile, 'a+')
        except:
           logger.print_info("logfile_fd maybe fail!\n")
        self.T1 = threading.Thread(target=self.log_to_file)
        self.T1.daemon = True
        self.T1.start()

    #@logger.print_line_info
    def write_data(self, data):
        self.threadLock.acquire()
        write_len = -1
        try:
            write_len = self.console.write(data)
            self.console.flushInput()
            '''if data != b'' and b'setenv default_env' in data:
              time.sleep(1)
              line = self.console.readline()
              logger.print_error(f"write_data read: {line}")'''
        except serial.SerialTimeoutException:
            logger.print_info("Failed to write data: No data can be written at this time.")
        self.threadLock.release()
        return write_len

    @logger.print_line_info
    def read_data(self, size=0):
        self.threadLock.acquire()
        data = 'NULL'
        try:
            if size == 0:
               data = self.console.readall()
            else:
               data = self.console.read(size)
            if data == '':
                logger.print_info("No data to read.")
        except serial.SerialTimeoutException:
            logger.print_info("Failed to read data: No data available at this time.")
        self.threadLock.release()
        return data

    def add_case_name_to_uartlog(self, add_prefix_buf, is_add_allline=True):
        self.add_prefix_buf = add_prefix_buf
        self.is_add_allline = is_add_allline

    def close(self):
        self.console.close()

    def open_case_uart_bak_file(self, bak_flie):
        self.case_uart_bak_file = bak_flie

    def close_case_uart_bak(self):
        self.case_uart_bak_file = ''

    def stop_record(self, timeout=1):
        logPrinter(mesg='stop_record ', log_obs=self.log_obs)
        self.serRunning = False
        self.T1.join(timeout)
        self.close()

    def set_check_keyword_list(self, keyword_list: list):
        self.keyword_list = keyword_list
        logger.print_info(f'set keywords:{self.keyword_list}')

    def clear_keyword_dict(self):
        self.keyword_dicts.clear()

    def add_keyword_dict(self, keyword_dict={}, opt=None):
        self.keyword_dicts |= keyword_dict

    def delete_keyword_dict(self, keyword=None):
        self.keyword_dicts.deld(keyword)

    def update_keyword_dict(self, keyword={}):
        self.keyword_dicts.deld(keyword)

    @logger.print_line_info
    def set_logfile(self, logfile=''):
        self.logfile = logfile
        self.crashlogFile = self.logfile.replace('.log', '') + '_crash.log'  # 串口log异常文件名
        logPrinter(mesg='set_logfile Log File "%s"' % self.logfile, log_obs=self.log_obs)
        # dir_path = self.logfile[:self.logfile.rfind('/')]
        dir_path = os.path.dirname(self.logfile)
        logPrinter("dir_path: %s" % dir_path, log_obs=self.log_obs)
        if not os.path.exists(dir_path):
            self.mkdir_path(dir_path)

    def set_is_hold_env(self, hold_env=True):
        self.hold_env = hold_env

    def get_case_have_keyword_dicts(self):
        return self.have_keyword_dicts

    def clear_case_have_keyword_dicts(self):
        self.have_keyword_dicts.clear()

    def get_quick_return(self):
        return self.quick_return

    def get_is_hold_env(self):
        if not self.hold_env:
            self.hold_flag = False
        return self.hold_flag

    def enable_check_keyword(self, ignore=True):
        self.ignore = ignore

    # 分析串口log是否有异常
    #@logger.print_line_info
    def analysis_log(self, line):
        warn_str = ''
        if len(self.keyword_list) > 0:
            for keyword in self.keyword_list:
                key_num = 0
                if keyword in line:
                    line = time.strftime('[%Y.%m.%d %H:%M:%S]', time.localtime(time.time())) + line.replace('\n',
                                                                                                            '').replace(
                        '\r', '') + '\n'
                    if child_node['action'] == 'hold_env':
                        self.hold_flag = True
                    elif child_node['action'] == 'return':
                        self.quick_return = True
                    key_num += 1
                    if key_num > 0:
                        if self.have_keyword_dicts.get(keyword):
                            self.have_keyword_dicts[keyword] += key_num
                        else:
                            self.have_keyword_dicts.setdefault(keyword, key_num)
                        warn_str = 'check_keywords:'
        if warn_str != '':
            with open(self.crashlogFile, 'a') as f:
                f.write(line)  # log异常
        return warn_str

    def count_curline_keyword_num(self, line):
        warn_str = ''
        if len(self.keyword_list) > 0:
            for keyword in self.keyword_list:
                    #logger.print_info(f"def cur_keyword:{keyword}! curline: {line}\n")
                    #logger.print_error(f"def cur_keyword:{keyword}! curline: {line}\n")
                    key_num = line.count(keyword)
                    if key_num > 0:
                        if self.have_keyword_dicts.get(keyword):
                            self.have_keyword_dicts[keyword] += key_num
                        else:
                            self.have_keyword_dicts.setdefault(keyword, key_num)
        return warn_str

    def in_waiting(self):
        return self.console.in_waiting

    def is_open(self):
        return self.console.is_open

    #@logger.print_line_info
    def set_check_keyword_and_send_cmd(self,wait_keyword='', cmd='', check_keyword='', send_times=1):
        #logger.print_info("set_check_keyword_and_send_cmd !\n")
        self.threadLock.acquire()
        self.wait_keyword = wait_keyword
        self.check_keyword = check_keyword
        if cmd == '':
           self.cmd = cmd + '\n' + '\n'
        else:
           self.cmd = cmd + '\n'
        self.send_times = send_times
        self.threadLock.release()

    #@logger.print_line_info
    def cmd_run_stat(self):
        return (self.is_run_cmd,self.check_keyword,self.ret_match_buffer)

    #@logger.print_line_info
    def clear_check_keyword_and_send_cmd(self):
        #logger.print_info("clear_check_keyword_and_send_cmd check_keyword:%s wait_keyword:%s!\n" %(self.check_keyword, self.wait_keyword))
        self.threadLock.acquire()
        self.is_run_cmd = False
        self.check_keyword = ''
        self.wait_keyword = ''
        self.cmd = ''
        self.ret_match_buffer = ''
        self.send_times = 0
        self.threadLock.release()

    def get_searia_buf(self):
        return self.uart_line_output

    # 调用子线程，记录串口log
    #@logger.print_line_info
    def log_to_file(self):
        while self.serRunning:
            if self.console.is_open:
                if self.console.in_waiting:
                    self.threadLock.acquire()
                    self.uart_line_output = self.uart_line = self.console.readline() #self.read_data()
                    self.threadLock.release()
                    try:
                        if isinstance(self.uart_line, bytes):
                           self.uart_line = self.uart_line.decode('utf-8').strip()
                        self.threadLock.acquire()
                        if self.board_state_in_boot_str != '' or self.board_state_in_kernel_str != '':
                           if self.uart_line == self.board_state_in_boot_str:
                               self.board_state = 'at uboot'
                           if self.uart_line == self.board_state_in_kernel_str:
                               self.board_state = 'at kernel'
                        if self.uart_line != '' and self.is_run_cmd and self.check_keyword != '':
                           if self.check_keyword in self.uart_line:
                               self.check_keyword = ''
                               self.ret_match_buffer = self.uart_line
                               logger.print_info(f"ret_match_buffer: {self.ret_match_buffer}\n")
                        self.threadLock.release()
                        self.write_line(self.uart_line)
                    except Exception as e:
                        logger.print_info(f'exception:{e} ==\n')
                        self.uart_line = 'expection'
                elif self.wait_keyword != '' and self.cmd != '' and self.wait_keyword in self.uart_line and self.is_run_cmd == False:
                     success_bytes = self.write_data(self.cmd.encode('utf-8'))
                     cmdlen = len(self.cmd.encode('utf-8'))
                     logger.print_info(f"send cmd: {self.cmd.encode('utf-8')} cmdlen:{cmdlen} success_bytes: {success_bytes}\n")
                     while success_bytes != len(self.cmd.encode('utf-8')):
                        success_bytes = self.write_data(self.cmd.encode('utf-8'))
                        logger.print_info("cmd:%s send fail success_bytes:%s %s\n" %(self.cmd.encode('utf-8'),success_bytes,len(self.cmd.encode('utf-8'))))
                        try_time += 1
                        if try_time > 4:
                            logger.print_error("cmd:%s send fail success_bytes:%s %s\n" %(self.cmd.encode('utf-8'),success_bytes,len(self.cmd.encode('utf-8'))))
                            self.send_time = 0
                            self.cmd = ''
                            break
                     self.send_time += 1
                     if self.send_time >= self.send_times:
                        self.is_run_cmd = True
                        self.send_time = 0
                        self.cmd = ''
                     self.threadLock.acquire()
                     self.uart_line_output = self.uart_line = self.console.readline() #self.read_data()
                     if isinstance(self.uart_line, bytes):
                         self.uart_line = self.uart_line.decode('utf-8').strip()
                     if self.is_run_cmd and self.check_keyword != '':
                           if self.check_keyword in self.uart_line:
                               self.ret_match_buffer = self.uart_line
                               self.check_keyword = ''
                               logger.print_info(f"ret_match_buffer: {self.ret_match_buffer}\n")
                     self.threadLock.release()
                     self.write_line(self.uart_line)
                     logger.print_info("log_to_file is_run_cmd:%s\n" %self.is_run_cmd)
                elif self.cmd != '' and self.wait_keyword=='no_check' and  self.is_run_cmd == False:
                     success_bytes = self.write_data(self.cmd.encode('utf-8'))
                     try_time = 0
                     logger.print_info(f"send cmd: {self.cmd.encode('utf-8')} success_bytes: {success_bytes}")
                     while success_bytes != len(self.cmd.encode('utf-8')):
                        success_bytes = self.write_data(self.cmd.encode('utf-8'))
                        try_time += 1
                        if try_time > 4:
                            logger.print_error("cmd:%s send fail success_bytes:%s %s\n" %(self.cmd.encode('utf-8'),success_bytes,len(self.cmd.encode('utf-8'))))
                            self.send_time = 0
                            self.cmd = ''
                            break
                     self.send_time += 1
                     if self.send_time >= self.send_times:
                        self.is_run_cmd = True
                        self.send_time = 0
                        self.cmd = ''
                     if self.is_run_cmd != True:
                        logger.print_error("is_run_cmd:%s\n" %self.is_run_cmd)
            time.sleep(0.001)


    # 将串口log写进文件中， 同时进行log的分析
    #@logger.print_line_info
    def write_line(self, line):
        if not self.ignore:
            # 检测串口log
            #ii = self.analysis_log(line)
            ii = self.count_curline_keyword_num(line)
        else:
            ii = ''
        self.isline_update = False
        with open(self.logfile, 'a+') as f:
            if line and line != '\r\n' and line != '\r':
                line = line.replace('\n', '').replace('\r', '') + '\n'
                if self.add_prefix_buf != '':
                   line = time.strftime('[%Y.%m.%d %H:%M:%S]', time.localtime(time.time())) +'['+ self.add_prefix_buf +']' + ii + line
                else:
                   line = time.strftime('[%Y.%m.%d %H:%M:%S]', time.localtime(time.time())) + ii + line
                #f.writelines(line)
                f.write(line)
                self.isline_update = True
                if self.case_uart_bak_file != '':
                    with open(self.case_uart_bak_file, 'a+') as fbak:
                       #fbak.writelines(line)
                       fbak.write(line)
                if self.is_add_allline == False:
                   self.add_prefix_buf = ''
                if self.is_rw_wdeta and self.wait_keyword != '' and self.cmd != '' and self.wait_keyword in line and self.is_run_cmd == False:
                     #self.cmd = self.cmd + '\n'
                     success_bytes = self.write_data(self.cmd.encode('utf-8'))
                     try_time = 0
                     logger.print_info(f"send cmd: {self.cmd.encode('utf-8')} success_bytes: {success_bytes}")
                     while success_bytes != len(self.cmd.encode('utf-8')):
                        success_bytes = self.write_data(self.cmd.encode('utf-8'))
                        try_time += 1
                        if try_time > 4:
                            logger.print_error("cmd:%s send fail success_bytes:%s %s\n" %(self.cmd.encode('utf-8'),success_bytes,len(self.cmd.encode('utf-8'))))
                            self.send_time = 0
                            self.cmd = ''
                            break
                     self.send_time += 1
                     if self.send_time >= self.send_times:
                        self.is_run_cmd = True
                        self.send_time = 0
                        self.cmd = ''
                     if not self.is_run_cmd:
                        logger.print_error("is_run_cmd:%s\n" %self.is_run_cmd)
                elif self.is_rw_wdeta and self.cmd != '' and self.wait_keyword=='no_check' and self.is_run_cmd == False:
                     success_bytes = self.write_data(self.cmd.encode('utf-8'))
                     try_time = 0
                     logger.print_info(f"send cmd: {self.cmd.encode('utf-8')} success_bytes: {success_bytes}")
                     while success_bytes != len(self.cmd.encode('utf-8')):
                        success_bytes = self.write_data(self.cmd.encode('utf-8'))
                        try_time += 1
                        if try_time > 4:
                            logger.print_error("cmd:%s send fail success_bytes:%s %s\n" %(self.cmd.encode('utf-8'),success_bytes,len(self.cmd.encode('utf-8'))))
                            self.send_time = 0
                            self.cmd = ''
                            break
                     self.send_time += 1
                     if self.send_time >= self.send_times:
                        self.is_run_cmd = True
                        self.send_time = 0
                        self.cmd = ''
                     if not self.is_run_cmd:
                        logger.print_error("is_run_cmd:%s\n" %self.is_run_cmd)

  # 将串口log写进文件中， 同时进行log的分析
    #@logger.print_line_info
    def write_line_old(self, line):
        if not self.ignore:
            # 检测串口log
            ii = self.analysis_log(line)
        else:
            ii = '[Ignore]'
        self.isline_update = False
        if self.logfile_fd:
            if line and line != '\r\n' and line != '\r':
                line = line.replace('\n', '').replace('\r', '') + '\n'
                if self.add_prefix_buf != '':
                   line = time.strftime('[%Y.%m.%d %H:%M:%S]', time.localtime(time.time())) +'['+ self.add_prefix_buf +']' + ii + line
                else:
                   line = time.strftime('[%Y.%m.%d %H:%M:%S]', time.localtime(time.time())) + ii + line
                #f.writelines(line)
                self.logfile_fd.writelines(line)
                self.isline_update = True
                if self.case_uart_bak_file != '':
                    with open(self.case_uart_bak_file, 'a+') as fbak:
                       fbak.writelines(line)
                if self.is_add_allline == False:
                   self.add_prefix_buf = ''
                if self.is_rw_wdeta and self.wait_keyword != '' and self.cmd != '' and self.wait_keyword in line and self.is_run_cmd == False:
                     success_bytes = self.write_data(self.cmd.encode('utf-8'))
                     try_time = 0
                     logger.print_info(f"send cmd: {self.cmd.encode('utf-8')} success_bytes: {success_bytes}")
                     while success_bytes != len(self.cmd.encode('utf-8')):
                        success_bytes = self.write_data(self.cmd.encode('utf-8'))
                        try_time += 1
                        if try_time > 4:
                            logger.print_error("cmd:%s send fail success_bytes:%s %s\n" %(self.cmd.encode('utf-8'),success_bytes,len(self.cmd.encode('utf-8'))))
                            self.send_time = 0
                            self.cmd = ''
                            break
                     self.send_time += 1
                     if self.send_time >= self.send_times:
                        self.is_run_cmd = True
                        self.send_time = 0
                        self.cmd = ''

                     if not self.is_run_cmd:
                        logger.print_error("is_run_cmd:%s\n" %self.is_run_cmd)

    #@logger.print_line_info
    def send_command(self, com, dely_time=0.001, cmdlen=-1, is_read=False):
        com = com + '\n'
        len = 0
        ret = 255
        is_waiting = False
        if isinstance(com, bytes):
           com = com.encode('utf-8')
        self.isline_update = False
        #logger.print_info("is_waiting:%s len:%s com:%s" %(is_waiting, len, com))
        write_len = self.write_data(com.encode('utf-8'))
        if self.console.is_open:
           if self.console.in_waiting:
              is_waiting = True
        if dely_time > 0:
           time.sleep(dely_time)
        #logger.print_info("is_waiting:%s len:%s com:%s" %(is_waiting, len, com))
        if is_read:
           output = self.read_data()
           logger.print_info("output:%s \n" % output)
           return output
        #logger.print_info("uart_line_output:%s \n" % self.uart_line_output)
        if cmdlen >= 0 and cmdlen == write_len-1:
           ret = 0
        return self.uart_line_output, write_len

    #@logger.print_line_info
    def command(self, com):
        # 执行串口命令
        com = com + '\n'
        com = com.encode('utf-8')
        self.write_data(com)
        time.sleep(1)
        output = self.console.readall()
        # 返回输出结果
        try:
            output = output.decode('utf-8')
            logPrinter(log_obs=self.log_obs, mesg='[COM %s] %s' % (self.port, output))
            output_list = output.split('\n')
            for line in output_list:
                self.write_line(line)
            for k in range(len(output_list)):
                output_list[k] = output_list[k].replace('\r', '')
            return output_list
        except Exception as e:
            logPrinter(mesg=str(e))
            return ''

    @logger.print_line_info
    def close(self):
        logPrinter(log_obs=self.log_obs,
                   mesg='[%s] Close SerialCtrl of DUT, COM %s' % (self.__class__.__name__, self.port))
        self.console.close()
        self.serRunning = False




# uartlog_contrl = _uartlog_contrl()
