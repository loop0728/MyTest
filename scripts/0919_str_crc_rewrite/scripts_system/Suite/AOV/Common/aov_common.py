import os

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

    def save_time_info(self, name, info) -> int:
        """
        根据case名称保存统计的时间信息

        Args:
            name (str): AOV case name
            info (str): test time infomation

        Returns:
            int: result
        """
        file = None
        result = 0
        filePath = "out/{}/time.txt".format(name)

        try:
            directory = os.path.dirname(filePath)
            os.makedirs(directory, exist_ok=True)
            file = open(filePath, "w")
            file.write(info)

        except FileNotFoundError:
            result = 255
        except PermissionError:
            result = 255
        finally:
            if file is not None:
                file.close()

        return result
