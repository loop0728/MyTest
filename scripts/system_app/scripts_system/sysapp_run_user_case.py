"""Entry point for executing cases."""
import sys
from suite.common.sysapp_common_logger import logger
from suite.common.sysapp_common_types import SysappErrorCodes
from suite.common.sysapp_common_error_codes import EVENT_HANDLERS


class SysappRunUserCase:
    """Run user Case entry."""
    def __init__(self, param_list):
        """
        Parameters required for the case.

        Args:
            case_run_cnt (int): case run cnt
            script_path (str): script path
            case_name (str): case name
            case_stage (str): case stage
        """
        self.script_path = param_list[1]
        self.case_name = param_list[2]
        self.case_stage = param_list[3]
        self.case_run_cnt = 1

        logger.info(f"module_path_name: {self.script_path}")
        logger.info(f"case_name: {self.case_name}")

    @staticmethod
    def snake_to_pascal(snake_str):
        """
        snake_case to PascalCase
        Args:
            snake_str (str): snake_case
        Returns:
            str : PascalCase
        """
        components = snake_str.split('_')
        return ''.join(x.capitalize() for x in components)

    def parase_case_run(self) -> int:
        """
        pass

        Args:
            pass (str): pass

        Returns:
            bool: result
        """
        result = SysappErrorCodes.FAIL
        calss_obj = ""
        module_path = "/".join(self.script_path.split("/")[:-1])
        module_name = self.script_path.split("/")[-1].split(".")[0]
        logger.info(f"module_path: {module_path}")
        logger.info(f"module_name: {module_name}")
        logger.info(f"case_name:{self.case_name}")

        sys.path.append(module_path)
        module = __import__(module_name)
        class_name = self.snake_to_pascal(module_name)
        calss_obj = getattr(module, class_name)  # get mode class
        if (
                self.case_name != "NULL"
                and self.case_name != ""
                and self.case_name != "help"
        ):
            instance = calss_obj(
                self.case_name,
                self.case_run_cnt,
                self.script_path
            )  # use class creat one instance
            instance.case_stage = self.case_stage
            if not instance:
                logger.error("create instance fail!")
        else:
            instance = calss_obj(
                module_name,
                self.case_run_cnt,
                self.script_path
            )  # use class creat one instance
            instance.case_stage = self.case_stage
            if not instance:
                logger.error("create instance fail!")
            instance.runcase_help()
            return 0
        try:
            result = instance.runcase()
        except Exception as e:
            logger.error(e)
        self.print_run_result(result)
        if result != SysappErrorCodes.SUCCESS:
            self.exception_handling(result)
        return result.value

    def print_run_result(self, result):
        """
        pass

        Args:
            pass (str): pass

        Returns:
            bool: result
        """
        if result != SysappErrorCodes.SUCCESS:
            logger.error(
                f"[AutoTest][{self.case_name}][fail][{result}][run_cnt:{self.case_run_cnt}]"
            )
        else:
            logger.warning(
                f"[AutoTest][{self.case_name}][pass][{result}][run_cnt:{self.case_run_cnt}]"
            )

    @staticmethod
    def exception_handling(err_code):
        """
        pass

        Args:
            err_code (Enum): Error Code

        Returns:
            bool: result
        """
        handler = EVENT_HANDLERS.get(err_code)
        if handler:
            handler()
        else:
            logger.warning("Unknown error code.")
        return err_code


def main(argv):
    """Run user case entry."""
    if len(argv) < 3:
        logger.error("run_user_case param num less 3")
        sys.exit(255)
    run_case_handle = SysappRunUserCase(argv)
    ret = run_case_handle.parase_case_run()
    return ret

if __name__ == "__main__":
    sys.exit(main(sys.argv))
