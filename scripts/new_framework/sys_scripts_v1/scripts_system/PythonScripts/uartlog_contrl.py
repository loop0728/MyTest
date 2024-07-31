#__all__ = ['_uartlog_contrl']

import sys
import threading
import serial
import time
import os
import platform
import io

from logger import logger

def logPrinter(mesg='Nothing to log.', log_obs=1):
    if log_obs:
        mesg = time.strftime('[%Y.%m.%d %H:%M:%S] ', time.localtime(time.time())) + str(mesg)
        logger.warning(mesg)


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
        self.logfile = logfile
        self.recordfile = io.StringIO()
        self.casefile = io.StringIO()
        self.cur_offset = 0
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
        self.is_rw_wdeta = True
        self.case_uart_bak_file = ''
        self.board_state = 'Unknow'
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

    def start_record(self):
        if self.logfile == '':
            self.logfile = './log/%s_%s.log' % (time.strftime('%Y%m%d_%H%M%S', time.localtime(time.time())), self.port)
        self.crashlogFile = self.logfile.replace('.log', '') + '_crash.log'  # 串口log异常文件名
        logPrinter(mesg='Create Log File "%s"' % self.logfile, log_obs=self.log_obs)
        self.recordfile = open(self.logfile, 'a+')
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
        self.T1 = threading.Thread(target=self.log_to_file)
        self.T1.daemon = True
        self.T1.start()

    def close(self):
        self.console.close()

    def open_case_uart_bak_file(self,bak_flie):
        self.case_uart_bak_file = bak_flie

    def close_case_uart_bak(self):
        self.case_uart_bak_file = ''

    def stop_record(self, timeout=1):
        logPrinter(mesg='stop_record ', log_obs=self.log_obs)
        self.serRunning = False
        self.T1.join(timeout)
        self.recordfile.close()
        self.close()

    def set_check_keyword_dict(self, keyword_dicts={}):
        self.keyword_dicts = keyword_dicts
        print(f'set keywords:{self.keyword_dicts}')

    def clear_keyword_dict(self):
        self.keyword_dicts.clear()

    def add_keyword_dict(self, opt=None, keyword_dict={}):
        self.keyword_dicts |= keyword_dict

    def delete_keyword_dict(self, keyword=None):
        self.keyword_dicts.deld(keyword)

    def update_keyword_dict(self, keyword={}):
        self.keyword_dicts.deld(keyword)

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

    def disable_check_keyword(self, ignore=True):
        self.ignore = ignore

    # 分析串口log是否有异常
    def analysis_log(self, line):
        warn_str = ''
        if self.keyword_dicts:
            for k, child_node in self.keyword_dicts.items():
                key_num = 0
                if k in line:
                    line = time.strftime('[%Y.%m.%d %H:%M:%S]', time.localtime(time.time())) + line.replace('\n',
                                                                                                            '').replace(
                        '\r', '') + '\n'
                    if child_node['action'] == 'hold_env':
                        self.hold_flag = True
                    elif child_node['action'] == 'return':
                        self.quick_return = True
                    key_num += 1
                    if key_num > 0:
                        if self.have_keyword_dicts.get(k):
                            self.have_keyword_dicts[k] += key_num
                        else:
                            self.have_keyword_dicts.setdefault(k, key_num)
                        warn_str = 'check_keywords:'
        if warn_str != '':
            with open(self.crashlogFile, 'a') as f:
                f.write(line)  # log异常
        return warn_str

    def in_waiting(self):
        return self.console.in_waiting

    def is_open(self):
        return self.console.is_open

    def set_check_keyword_and_send_cmd(self,check_keyword='', cmd='', send_times=1):
        self.check_keyword = check_keyword
        self.cmd = cmd
        self.send_times = send_times

    def is_run_cmd(self) -> bool:
        return self.is_run_cmd

    def clear_check_keyword_and_send_cmd(self):
        self.is_run_cmd = False
        self.check_keyword = ''
        self.cmd = ''
        self.send_times = 0

    def open_serial_buf(self):
        self.casefile = open(self.logfile, 'r')
        self.casefile.seek(0, 2)

    def close_serial_buf(self):
        self.recordfile.flush()
        self.casefile.close()

    def get_serial_buf(self):
        return self.casefile.readline()

    def get_searia_buf(self):
        return self.uart_line_output

    # 调用子线程，记录串口log
    def log_to_file(self):
        while self.serRunning:
            if self.console.is_open:
                if self.console.in_waiting:
                    self.threadLock.acquire()
                    self.uart_line_output = self.uart_line = self.console.readline()
                    self.threadLock.release()
                    try:
                        self.uart_line = self.uart_line.decode('utf-8').strip()
                        if self.board_state_in_boot_str != '' or self.board_state_in_kernel_str != '':
                           if self.uart_line == self.board_state_in_boot_str:
                               self.board_state = 'at uboot'
                           if self.uart_line == self.board_state_in_kernel_str:
                               self.board_state = 'at kernel'
                        self.write_line(self.uart_line)
                    except Exception as e:
                        print(f'exception:{e} ==\n')
                        self.uart_line = 'expection'
                elif self.check_keyword != '' and self.cmd != '' and self.check_keyword in self.uart_line and self.is_run_cmd == False:
                     success_bytes = self.console.write(self.cmd.encode('utf-8'))
                     while success_bytes != len(self.cmd.encode('utf-8')):
                        success_bytes = self.console.write(self.cmd.encode('utf-8'))
                        try_time += 1
                        if try_time > 4:
                            logger.error("cmd:%s send fail success_bytes:%s %s\n" %(self.cmd.encode('utf-8'),success_bytes,len(self.cmd.encode('utf-8'))))
                            self.send_time = 0
                            break
                     self.send_time += 1
                     if self.send_time >= self.send_times:
                        self.is_run_cmd = True
                        self.send_time = 0
                     logger.warning("is_run_cmd:%s\n" %self.is_run_cmd)
    # 将串口log写进文件中， 同时进行log的分析
    def write_line(self, line):
        if not self.ignore:
            # 检测串口log
            ii = self.analysis_log(line)
        else:
            ii = '[Ignore]'
        if line and line != '\r\n' and line != '\r':
            line = line.replace('\n', '').replace('\r', '') + '\n'
            line = time.strftime('[%Y.%m.%d %H:%M:%S]', time.localtime(time.time())) + ii + line
            self.recordfile.writelines(line)
            self.recordfile.flush()
            if self.is_rw_wdeta and self.check_keyword != '' and self.cmd != '' and self.check_keyword in line and self.is_run_cmd == False:
                success_bytes = self.console.write(self.cmd.encode('utf-8'))
                try_time = 0
                while success_bytes != len(self.cmd.encode('utf-8')):
                    success_bytes = self.console.write(self.cmd.encode('utf-8'))
                    try_time += 1
                    if try_time > 4:
                        logger.error("cmd:%s send fail success_bytes:%s %s\n" %(self.cmd.encode('utf-8'),success_bytes,len(self.cmd.encode('utf-8'))))
                        self.send_time = 0
                        break
                self.send_time += 1
                if self.send_time >= self.send_times:
                    self.is_run_cmd = True
                    self.send_time = 0
                logger.warning("is_run_cmd:%s\n" %self.is_run_cmd)
            if self.case_uart_bak_file != '':
                with open(self.case_uart_bak_file, 'a+') as fbak:
                    fbak.writelines(line)

    def send_command(self, com ,dely_time = 0.001):
        com = com + '\n'
        self.threadLock.acquire()
        com = com.encode('utf-8')
        if dely_time > 0:
           time.sleep(dely_time)
        self.console.write(com)
        self.threadLock.release()

    def command(self, com):
        # 执行串口命令
        com = com + '\n'
        com = com.encode('utf-8')
        self.threadLock.acquire()
        self.console.write(com)
        time.sleep(1)
        output = self.console.readall()
        self.threadLock.release()
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

    def close(self):
        logPrinter(log_obs=self.log_obs,
                   mesg='[%s] Close SerialCtrl of DUT, COM %s' % (self.__class__.__name__, self.port))
        self.console.close()
        self.serRunning = False




# uartlog_contrl = _uartlog_contrl()
