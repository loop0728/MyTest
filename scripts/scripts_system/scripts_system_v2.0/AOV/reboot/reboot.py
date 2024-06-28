import sys
import time
import re
import os
import json
from logger import logger
import threading
import inspect

class reboot_case():
    cnt_check_keyword_dict = {}

    def __init__(self, client_handle, case_name, case_log_path, case_run_cnt=1):
        self.case_name = case_name
        self.borad_cur_state = ''
        self.client_handle = client_handle
        self.protocol = 'uart'
        self.case_run_cnt = int(case_run_cnt)
        self.client_running = False
        self.reboot_way = ''
        self.return_way = 'still_case_run_cnt_to_0' #'have_fail_return'
        self.client_handle.add_case_name_to_uartlog()           
        self.case_log_path = case_log_path.replace('uart.log', '') + case_name + '_uart.log'
        self.client_handle.open_case_uart_bak_file(self.case_log_path)
        self.set_check_keyword_dict = {}
        self.other_case_json_path = './AOV/reboot/reboot_keyword.json'
        self.reboot_timeout = 180
        
        super().__init__()

    def get_server_data(self):  
        if self.protocol == 'uart':
           self.client_handle.still_send_uartlog_data()   
        elif self.protocol == 'telnet':
           self.client_handle.still_send_telnet_data()  
        while self.client_running:
            cur_server_data = self.client_handle.client_get_server_data()
            if isinstance(cur_server_data, bytes):
               cur_server_data = cur_server_data.decode('utf-8')
            logger.print_info(f"responsemsg: {cur_server_data}")     
            time.sleep(0.1)

    def open_get_uart_log_thread(self):
       self.client_running = True
       self.client_handler = threading.Thread(target=self.get_server_data)
       self.client_handler.daemon = True
       self.client_handler.start()

    def stop_get_server_data(self, timeout=15):  
        self.client_running = False
        self.client_handler.join(timeout)
    
    @logger.print_line_info
    def cold_reboot(self):
       if self.case_run_cnt <= 0:
          logger.print_error(f"case run time more than {self.case_run_cnt} !\n")
          return result
       set_check_keyword_list = []
       for keyword,num in self.set_check_keyword_dict.items():
           set_check_keyword_list.append(keyword)
       self.client_handle.client_set_check_uartlog_keyword_arr('set_check_uartlog_keyword_list', set_check_keyword_list)
       self.client_handle.cold_reboot()
       self.client_handle.clear_borad_cur_state()
       uartlog_curline = self.client_handle.get_borad_uartlogline()
       time.sleep(1)
       trywait_time = 0
       result = 255
       while True:
          self.borad_cur_state = self.client_handle.get_borad_cur_state()
          if self.borad_cur_state == 'at kernel':
               result = 0
               break
          elif self.borad_cur_state == 'at uboot':
               break
          trywait_time = trywait_time + 1
          if trywait_time > 180:
             break
          time.sleep(1)
       ret,uart_keyword_dict = self.client_handle.client_get_check_uartlog_keyword_dict('get_check_uartlog_keyword_dict', set_check_keyword_list)
       if len(uart_keyword_dict) > 0 and len(set_check_keyword_list) > 0:
          for keyword,num in uart_keyword_dict.items():
             last_cnt = 0
             if self.cnt_check_keyword_dict.get(keyword):
                last_cnt = int(self.cnt_check_keyword_dict[keyword])
             if keyword in set_check_keyword_list and num-last_cnt > int(self.set_check_keyword_dict[keyword]):
                result = 255
             if self.cnt_check_keyword_dict.get(keyword):
                self.cnt_check_keyword_dict[keyword] = num
             else:
                self.cnt_check_keyword_dict.setdefault(keyword, num) 
             logger.print_error(f'keyword:{keyword}, sum_cnt:{num}, cur_cnt:{num-last_cnt}!\n')
       return result              
    
    @logger.print_line_info
    def uboot_rest_reboot(self):
       trywait_time = 0
       result = 255
       if self.case_run_cnt <= 0:
          logger.print_error(f"case run time more than {self.case_run_cnt} !\n")
          return result
       uboot_rest_reboot_mode = 'reboot' #reboot
       set_check_keyword_list = []
       for keyword,num in self.set_check_keyword_dict.items():
           set_check_keyword_list.append(keyword)
       self.client_handle.client_set_check_uartlog_keyword_arr('set_check_uartlog_keyword_list', set_check_keyword_list)
       self.client_handle.client_send_cmd_to_server('')
       uartlog_curline = self.client_handle.get_borad_uartlogline()
       self.borad_cur_state = self.client_handle.get_borad_cur_state()
       if self.borad_cur_state == 'Unknow':
          for i in range(1,20):
             self.client_handle.client_send_cmd_to_server('')
             self.borad_cur_state = self.client_handle.get_borad_cur_state()   
             if self.borad_cur_state != 'Unknow':
                break
       if self.borad_cur_state == 'Unknow':
          return result
       if self.borad_cur_state == 'at uboot':
          self.client_handle.clear_borad_cur_state() 
          self.client_handle.client_send_cmd_to_server('reset')
       if self.borad_cur_state == 'at kernel':
          self.client_handle.clear_borad_cur_state() 
          if uboot_rest_reboot_mode == 'cold_reboot':
             self.client_handle.cold_reboot()
          else:
             self.client_handle.client_send_cmd_to_server('reboot')
             #time.sleep(1)
             self.client_handle.clear_borad_cur_state()
          for i in range(1,20):
             self.client_handle.client_send_cmd_to_server('')
             self.borad_cur_state = self.client_handle.get_borad_cur_state()
             time.sleep(0.01)
             if self.borad_cur_state == 'at uboot':
                self.client_handle.clear_borad_cur_state() 
                time.sleep(0.1)
                self.client_handle.client_send_cmd_to_server('reset')
                break 
       logger.print_info(self.borad_cur_state)
       while True:
         self.borad_cur_state = self.client_handle.get_borad_cur_state()
         if self.borad_cur_state == 'at kernel':
           logger.print_info("borad_cur_state:%s \n" % self.borad_cur_state) 
           result = 0
           break
         elif self.borad_cur_state == 'at uboot':
           self.client_handle.clear_borad_cur_state() 
           self.client_handle.client_send_cmd_to_server('reset')
           continue
         else:
           time.sleep(1)
           #logger.print_info("borad_cur_state:%s \n" % self.borad_cur_state) 
           trywait_time = trywait_time + 1
           if trywait_time > 180:
             break
       ret,uart_keyword_dict = self.client_handle.client_get_check_uartlog_keyword_dict('get_check_uartlog_keyword_dict', set_check_keyword_list)
       if len(uart_keyword_dict) > 0 and len(set_check_keyword_list) > 0:
          for keyword,num in uart_keyword_dict.items():
             last_cnt = 0
             if self.cnt_check_keyword_dict.get(keyword):
                last_cnt = int(self.cnt_check_keyword_dict[keyword])
             if keyword in set_check_keyword_list and num-last_cnt > int(self.set_check_keyword_dict[keyword]):
                result = 255
             if self.cnt_check_keyword_dict.get(keyword):
                self.cnt_check_keyword_dict[keyword] = num
             else:
                self.cnt_check_keyword_dict.setdefault(keyword, num) 
             logger.print_error(f'keyword:{keyword}, sum_cnt:{num}, cur_cnt:{num-last_cnt}!\n')
       return result       
    
    @logger.print_line_info
    def kernel_reboot(self):
       trywait_time = 0
       result = 255
       if self.case_run_cnt <= 0:
          logger.print_error(f"case run time more than {self.case_run_cnt} !\n")
          return result
       logger.print_info("goto kernel_reboot \n")  
       set_check_keyword_list = []
       for keyword,num in self.set_check_keyword_dict.items():
           set_check_keyword_list.append(keyword)
       self.client_handle.client_set_check_uartlog_keyword_arr('set_check_uartlog_keyword_list', set_check_keyword_list)
       self.client_handle.client_send_cmd_to_server('')
       uartlog_curline = self.client_handle.get_borad_uartlogline()
       self.borad_cur_state = self.client_handle.get_borad_cur_state()
       if self.borad_cur_state == 'Unknow':
          for i in range(1,20):
             self.client_handle.client_send_cmd_to_server('')
             self.borad_cur_state = self.client_handle.get_borad_cur_state()   
             if self.borad_cur_state != 'Unknow':
                break
       if self.borad_cur_state == 'Unknow':
          return result   
       if self.borad_cur_state == 'at kernel':
           self.client_handle.client_send_cmd_to_server('reboot')
           time.sleep(2)
           self.client_handle.clear_borad_cur_state()             
       while True:
          self.borad_cur_state = self.client_handle.get_borad_cur_state()
          if self.borad_cur_state == 'at kernel':
             result = 0
             logger.print_info("borad_cur_state:%s \n" % self.borad_cur_state) 
             break
          elif self.borad_cur_state == 'at uboot':
             self.client_handle.client_send_cmd_to_server('reset')
             self.client_handle.clear_borad_cur_state()
             result = 0
          else:
             time.sleep(1)
             #logger.print_info("borad_cur_state:%s \n" % self.borad_cur_state) 
             trywait_time = trywait_time + 1
             if trywait_time > 180:
                break
       ret,uart_keyword_dict = self.client_handle.client_get_check_uartlog_keyword_dict('get_check_uartlog_keyword_dict', set_check_keyword_list)
       if len(uart_keyword_dict) > 0 and len(set_check_keyword_list) > 0:
          for keyword,num in uart_keyword_dict.items():
             last_cnt = 0
             if self.cnt_check_keyword_dict.get(keyword):
                last_cnt = int(self.cnt_check_keyword_dict[keyword])
             if keyword in set_check_keyword_list and num-last_cnt > int(self.set_check_keyword_dict[keyword]):
                result = 255
             if self.cnt_check_keyword_dict.get(keyword):
                self.cnt_check_keyword_dict[keyword] = num
             else:
                self.cnt_check_keyword_dict.setdefault(keyword, num) 
             logger.print_error(f'keyword:{keyword}, sum_cnt:{num}, cur_cnt:{num-last_cnt}!\n')
       return result   

    def check_keyword_reboot(self):        
       trywait_time = 0
       result = 255
       if self.case_run_cnt <= 0:
          logger.print_error(f"case run time more than {self.case_run_cnt} !\n")
          return result
       self.case_run_cnt = self.case_run_cnt - 1
       logger.print_info("goto check_keyword_reboot!\n")
       if len(self.set_check_keyword_dict) <= 0:
          return result
       set_check_keyword_list = []
       for keyword,num in self.set_check_keyword_dict.items():
           set_check_keyword_list.append(keyword)
       self.client_handle.client_set_check_uartlog_keyword_arr('set_check_uartlog_keyword_list', set_check_keyword_list)
       if 'cold_reboot' == self.reboot_way:
          self.client_handle.cold_reboot()
       else:
          self.client_handle.client_send_cmd_to_server('')       
          self.borad_cur_state = self.client_handle.get_borad_cur_state()
          if self.borad_cur_state == 'Unknow':
             for i in range(1,20):
                self.client_handle.client_send_cmd_to_server('')
                self.borad_cur_state = self.client_handle.get_borad_cur_state()   
                if self.borad_cur_state != 'Unknow':
                   break
             if self.borad_cur_state == 'Unknow':
                return result   
          if self.borad_cur_state == 'at kernel':
             self.client_handle.client_send_cmd_to_server('reboot')  
             time.sleep(1)
             self.client_handle.clear_borad_cur_state()               
       while True:
         self.borad_cur_state = self.client_handle.get_borad_cur_state()
         if self.borad_cur_state == 'at kernel':
              result = 0
              logger.print_info("borad_cur_state:%s \n" % self.borad_cur_state) 
              break
         elif self.borad_cur_state == 'at uboot':
           self.client_handle.client_send_cmd_to_server('reset')
           self.client_handle.clear_borad_cur_state()
           result = 0
         else:
           time.sleep(1)
           #logger.print_info("borad_cur_state:%s \n" % self.borad_cur_state) 
           trywait_time = trywait_time + 1
           if trywait_time > self.reboot_timeout:
              break

       ret,uart_keyword_dict = self.client_handle.client_get_check_uartlog_keyword_dict('get_check_uartlog_keyword_dict', set_check_keyword_list)
       if len(uart_keyword_dict) > 0 and len(set_check_keyword_list) > 0:
          for keyword,num in uart_keyword_dict.items():
             last_cnt = 0
             if self.cnt_check_keyword_dict.get(keyword):
                last_cnt = int(self.cnt_check_keyword_dict[keyword])
             if keyword in set_check_keyword_list and num-last_cnt > int(self.set_check_keyword_dict[keyword]):
                result = 255
             if self.cnt_check_keyword_dict.get(keyword):
                self.cnt_check_keyword_dict[keyword] = num
             else:
                self.cnt_check_keyword_dict.setdefault(keyword, num) 
             logger.print_error(f'keyword:{keyword}, sum_cnt:{num}, cur_cnt:{num-last_cnt}!\n')
       return result    

    @logger.print_line_info
    def other_case(self):
        logger.print_info("go to other_case!\n")
        result = 255
        if os.path.exists(self.other_case_json_path):
            with open(self.other_case_json_path, "r", encoding='utf-8') as f:
                 content = json.load(f)
                 if self.reboot_way in content.keys():
                    self.set_check_keyword_dict = content[self.reboot_way]['check_keyword_list']
                    #logger.print_error(self.set_check_keyword_dict)
                    self.set_check_keyword_dict = eval(self.set_check_keyword_dict)
        else:
            return result
        if self.reboot_way == 'kernel_reboot':
            result = self.kernel_reboot()
        elif self.reboot_way == 'cold_reboot':
            result = self.cold_reboot()
        elif self.reboot_way == 'uboot_rest_reboot':
            result = self.uboot_rest_reboot()
        else:
            return result
        #result = self.check_keyword_reboot()
        return result

    @logger.print_line_info
    def runcase(self):
       result = 255
       self.set_check_keyword_dict = {'bug on':0, 'unknown symbol': 0, 'Call trace':0, 'Exception stack':0, 'oom-killer':0, 'fifo full bypass':0, 'Sensor is abnormal':0}
       if self.case_name == 'cold_reboot':    
         result = self.cold_reboot()
       elif self.case_name == 'kernel_reboot':   
         result = self.kernel_reboot()
       elif self.case_name == 'uboot_rest_reboot':   
         result = self.uboot_rest_reboot()
       else:
         print(self.case_name)
         if 'reboot_bugon_fifofull' in self.case_name:
            if self.case_name == 'kernel_reboot_bugon_fifofull':
               self.reboot_way = 'kernel_reboot'
               self.set_check_keyword_dict = {'bug on':'100','fifofull':'0'}
               result = self.kernel_reboot()
            elif self.case_name == 'cold_reboot_bugon_fifofull':
               self.reboot_way = 'cold_reboot'  
               self.set_check_keyword_dict = {'bug on':'100','fifofull':'0'}
               result = self.cold_reboot()
            elif self.case_name == 'uboot_rest_reboot_bugon_fifofull':
               self.reboot_way = 'uboot_rest_reboot'  
               self.set_check_keyword_dict = {'bug on':'100','fifofull':'0'}
               result = self.uboot_rest_reboot()            
            #result = self.check_keyword_reboot()
         else:
            if 'kernel_reboot' in self.case_name:
               self.reboot_way = 'kernel_reboot'
            elif 'cold_reboot' in self.case_name:
               self.reboot_way = 'cold_reboot'
            elif 'uboot_rest_reboot' in self.case_name:
               self.reboot_way = 'uboot_rest_reboot'
            else:
               return result
            result = self.other_case()
       return result


@logger.print_line_info
def system_runcase(args, client_handle):
    if len(args) < 3:
       logger.print_error(f"len:{len(args)} {args[0]} {args[1]} {args[2]} \n")
       return 255
    input_case_name = args[0]
    case_run_cnt = args[1] 
    case_log_path = args[2]
    if input_case_name[len(input_case_name)-1:].isdigit() and '_stress_' in input_case_name:
       parase_list = input_case_name.split('_stress_')
       if len(parase_list) != 2:
          return 255
       print(f"parase_list:{parase_list}!\n")
       case_run_cnt = int(parase_list[1])
       case_name = parase_list[0]
       logger.print_info(f"case_run_cnt: {case_run_cnt} case_name:{case_name}\n")
    else:
       case_name = input_case_name
    ret_str = '[Fail]'
    result = 255
    if int(case_run_cnt) > 0:   
       ret = 0
       for cnt in range(0, int(case_run_cnt)):
         rebootcase_handle = reboot_case(client_handle, case_name, case_log_path, case_run_cnt)
         if int(case_run_cnt) > 1:
             tmp_case_name = input_case_name+':'+ '{}'.format(cnt+1)
             client_handle.add_case_name_to_uartlog(tmp_case_name)
         ret |= rebootcase_handle.runcase()     
         if ret == 0:
            ret_str = '[success][cnt={}][maxcnt={}]'.format(cnt+1, case_run_cnt)
            logger.print_info("[AUTO_TEST][%s][%s][ret:%s]:" %(case_name, ret_str, ret))
         else:
            ret_str = '[Fail][cnt={}][maxcnt={}]'.format(cnt+1, case_run_cnt)
            logger.print_info("[AUTO_TEST][%s][%s][ret:%s]:" %(case_name, ret_str, ret))
            if rebootcase_handle.return_way == 'have_fail_return':
               return ret
         result = ret
       client_handle.client_close()
    else:
       logger.print_info("[AUTO_TEST][%s][%s][ret:%s]:" %(case_name, ret_str, result))
    return result

@logger.print_line_info
def system_help(args):
    logger.print_warning("only for reboot cold_reboot kernel_reboot uboot_rest_reboot\n")
    logger.print_warning("python client.py ./AOV/reboot/reboot.py reboot 2\n")