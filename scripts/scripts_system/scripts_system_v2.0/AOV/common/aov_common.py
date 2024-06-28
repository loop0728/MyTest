import time

from uart_record import uartlog_contrl_handle

# 全局变量定义
RESULT_PASS = 0
RESULT_FAIL = 255
WAIT_TIME = 20             # reset wait time

class AOVCase():
    """
    AOV case

    Attributes:
        name: case name
    """
    def __init__(self, name):
        """
        init func

        Args:
            name: AOV case name
        """
        self.name = name

    def goto_kernel(self):
        """
        进入 kernel cmdline

        Args:
            NA

        Returns:
            int:
            RESULT_PASS: 进入kernel成功
            RESULT_FAIL: 进入kernel失败
        """
        result = RESULT_PASS
        try_cnt = 0
        uartlog_contrl_handle.send_command("\n")
        while True:
            cur_env = uartlog_contrl_handle.get_borad_cur_state()
            if cur_env == 'at uboot':
                uartlog_contrl_handle.send_command("reset")
            elif cur_env == 'at kernel':
                print("[sys_app] at kernel!\n")
                break
            time.sleep(WAIT_TIME)
            try_cnt = try_cnt + 1
            if try_cnt > 3:
                print("goto kernel timeout!\n")
                return RESULT_FAIL
        return result

    def quit_demo(self):
        """
        退出aov demo

        Args:
            NA

        Returns:
            int:
            RESULT_PASS: 退出demo成功
            RESULT_FAIL: 退出demo失败
        """
        uartlog_contrl_handle.send_command("\003")
        time.sleep(2)
        uartlog_contrl_handle.send_command("\n")
        time.sleep(5)
        uartlog_contrl_handle.send_command("cd /")
        cur_env = uartlog_contrl_handle.get_borad_cur_state()
        if cur_env == 'at kernel':
            return RESULT_PASS
        else:
            return RESULT_FAIL