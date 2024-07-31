import sys
import time
import threading
from logger import logger

from uart_record import uartlog_contrl_handle
sys.path.append("..")
from AOV.common.aov_common import AOVCase

# 全局变量定义
RESULT_PASS = 0
RESULT_FAIL = 255
WAIT_TIMEOUT = 10         # 下发命令等待demo回复的超时时间 Second
DEFAULT_TIME = 0          # 初始化默认时间 ms
THRESHOLD_TIME = 1000     # 阈值时间 ms

KeyWord="[AUTO TEST]TargetBufferGet cost"

def TargetBufferGetTime():
    """ 获取检测到人形之后得到buffer的时间 """
    global BufferGetTime
    BufferGetTime = DEFAULT_TIME
    while True:
        # 获取串口一行信息
        cur_line = uartlog_contrl_handle.get_searia_buf()
        # 如果是字节串，则解码成字符串
        if isinstance(cur_line, bytes):
            cur_line = cur_line.decode('utf-8').strip()

        if KeyWord in cur_line:
            value = cur_line.split('=')[1].strip()
            BufferGetTime = int(value)
            break
    return BufferGetTime

def CompBufferGetTime(BufferGetTime):
    """ 判断时间是否满足要求 """
    result = RESULT_PASS
    if BufferGetTime == DEFAULT_TIME:
        logger.error("[sys_app] get time fail!\n")
        result = RESULT_FAIL
    if  BufferGetTime > THRESHOLD_TIME:
        logger.error("[sys_app] {} > {}\n".format(BufferGetTime, THRESHOLD_TIME))
        result = RESULT_FAIL
    return result

def system_runcase(args):
    Case_Name = args[0]
    print("caseName:", Case_Name)
    result = RESULT_PASS
    result_tmp = RESULT_PASS
    global BufferGetTime
    BufferGetTime = DEFAULT_TIME

    change_fps = AOVCase(Case_Name)
    # step0 进入kernel
    result = change_fps.goto_kernel()
    if result != RESULT_PASS:
        return result
    # step1 进入aov demo
    uartlog_contrl_handle.send_command("cd /customer/sample_code/bin/")
    time.sleep(1)
    uartlog_contrl_handle.send_command("./prog_aov_aov_demo -t")
    time.sleep(10)
    # step2 开一个线程获取切换时间
    BufferGetTime_t = threading.Thread(target=TargetBufferGetTime)
    BufferGetTime_t.start()
    # step3 下发高低帧率切换命令
    uartlog_contrl_handle.send_command("a")
    time.sleep(WAIT_TIMEOUT)
    # step4 判断时间是否正确
    result_tmp = CompBufferGetTime(BufferGetTime)
    if result_tmp != RESULT_PASS:
        logger.error("[sys_app] {} get time FAIL!\n".format(Case_Name))
        result = result_tmp
    else:
        logger.info("[sys_app] time is {}ms!\n".format(BufferGetTime))
    # step5 退出aov demo
    result_tmp = change_fps.quit_demo()
    if result_tmp != RESULT_PASS:
        logger.error("[sys_app] {} quit aov demo FAIL!\n".format(Case_Name))
        result = result_tmp
    return result

def system_help(args):
    print("change fps case")
