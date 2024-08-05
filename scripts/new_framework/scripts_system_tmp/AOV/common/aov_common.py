import os
import time


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

    def save_time_info(self, name, info):
        """
        根据case名称保存统计的时间信息

        Args:
            name: AOV case name
            info: test time infomation

        Returns:
            int:
            RESULT_PASS: 保存信息成功
            RESULT_FAIL: 保存信息失败
        """
        file = None
        result = RESULT_PASS
        filePath = "out/{}/time.txt".format(name)

        try:
            directory = os.path.dirname(filePath)
            os.makedirs(directory, exist_ok=True)
            file = open(filePath, "w")
            file.write(info)

        except FileNotFoundError:
            result = RESULT_FAIL
        except PermissionError:
            result = RESULT_FAIL
        finally:
            if file is not None:
                file.close()

        return result
