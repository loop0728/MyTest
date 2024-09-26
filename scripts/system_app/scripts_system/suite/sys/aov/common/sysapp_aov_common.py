"""Common Class for aov case."""
import os

class SysappAovCommon():
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

    @staticmethod
    def save_time_info(name, info) -> int:
        """
        Save time info to "out/case_name/time.txt".

        Args:
            name (str): AOV case name
            info (str): test time infomation

        Returns:
            int: result
        """
        file = None
        result = 0
        file_path = f"out/{name}/time.txt"

        try:
            directory = os.path.dirname(file_path)
            os.makedirs(directory, exist_ok=True)
            with open(file_path, "w", encoding='utf-8') as file:
                file.write(info)

        except FileNotFoundError:
            result = 255
        except PermissionError:
            result = 255

        return result
