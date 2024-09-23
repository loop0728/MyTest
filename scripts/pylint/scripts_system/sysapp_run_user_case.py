"""Entry point for executing cases."""
import sys
from python_scripts.logger import logger
from common.sysapp_common_error_codes import event_handlers


class RunUserCase:
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

        logger.print_info(f"module_path_name: {self.script_path}")
        logger.print_info(f"case_name: {self.case_name}")

    def parase_case_run(self) -> int:
        """
        pass

        Args:
            pass (str): pass

        Returns:
            bool: result
        """
        result = 255
        calss_obj = ""
        module_path = "/".join(self.script_path.split("/")[:-1])
        module_name = self.script_path.split("/")[-1].split(".")[0]
        case_name = self.case_name
        logger.print_info(f"module_path: {module_path}")
        logger.print_info(f"module_name: {module_name}")

        sys.path.append(module_path)
        module = __import__(module_name)
        logger.print_info(f"case_name:{self.case_name}")
        calss_obj = getattr(module, case_name)  # get mode class
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
                logger.print_error("create instance fail!")
        else:
            instance = calss_obj(
                module_name,
                self.case_run_cnt,
                self.script_path
            )  # use class creat one instance
            instance.case_stage = self.case_stage
            if not instance:
                logger.print_error("create instance fail!")
            instance.runcase_help()
            return 0
        try:
            result = instance.runcase()
        except Exception as e:
            logger.print_error(e)
        self.print_run_result(result)
        if result != 0:
            self.exception_handling(result)
        return result

    def print_run_result(self, result):
        """
        pass

        Args:
            pass (str): pass

        Returns:
            bool: result
        """
        if result:
            logger.print_warning(
                f"[AutoTest][{self.case_name}][fail][{result}][run_cnt:{self.case_run_cnt}]"
            )
        else:
            logger.print_warning(
                f"[AutoTest][{self.case_name}][pass][{result}][run_cnt:{self.case_run_cnt}]"
            )

    def exception_handling(self, err_code):
        """
        pass

        Args:
            err_code (Enum): Error Code

        Returns:
            bool: result
        """
        handler = event_handlers.get(err_code)
        if handler:
            handler()
        else:
            logger.print_warning("Unknown error code.")
        return err_code


if __name__ == "__main__":
    if len(sys.argv) < 3:
        logger.print_error("run_user_case param num less 3")
        sys.exit(255)
    run_case_handle = RunUserCase(sys.argv)
    ret = run_case_handle.parase_case_run()
    sys.exit(ret)
