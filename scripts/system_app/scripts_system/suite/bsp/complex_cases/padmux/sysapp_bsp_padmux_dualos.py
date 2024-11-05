"""Padmux case in Dualos scnce"""
from suite.common.sysapp_common_logger import logger, sysapp_print
from suite.common.sysapp_common_case_base import SysappCaseBase as CaseBase
from suite.common.sysapp_common_types import SysappErrorCodes as EC
from suite.bsp.complex_cases.padmux.sysapp_bsp_padmux_base import SysappBspPadmuxBase as PadmuxBase
from sysapp_client import SysappClient


class SysappBspPadmuxDualos(CaseBase):
    """Pin-mode Indicates the behavior detection case in the dualos scenario

    Test Info
    1.Detects the pin-mode setting behavior of boot.bin in the dualos scenario
    2.Detects the pin-mode setting behavior of rtos in the dualos scenario
    3.Detects the pin-mode setting behavior of kernel in the dualos scenario

    Attributes:
            case_name (str): case name
            case_run_cnt (int): case run cnt
            script_path (str): script_path
            case_stage (char): case stage
    """

    def __init__(self, case_name, case_run_cnt=1, script_path="./"):
        """Case Init function

        Args:
            case_name: case name
            case_run_cnt: case run cnt
            script_path: script_path
            case_stage: case stage
        """
        super().__init__(case_name, case_run_cnt, script_path)
        self.case_name = case_name
        self.case_run_cnt = case_run_cnt
        # self.script_path = script_path
        self.uart = SysappClient(self.case_name, "uart", "uart")
        self.padmux_handle = PadmuxBase(self.uart)
        self.flag_judge_bootbin = True
        self.flag_judge_kernel = True
        self.flag_judge_rtos = True
        logger.info(f"{self.case_name} init successful")

    @sysapp_print.print_line_info
    def judge_fail_result(self):
        """Result failure judgment

        Args:
            Na
        """
        self.flag_judge_bootbin = False
        self.flag_judge_kernel = False
        self.flag_judge_rtos = False
        logger.info("run judge_fail_result succeed")
        return True

    @sysapp_print.print_line_info
    def runcase(self):
        """Run case entry.

        Args:
            Na

        Returns:
            enum: ErrorCodes code
        """
        err_code = EC.SUCCESS
        info_err = []
        try:

            ret = self.padmux_handle.prepare_for_test_environment(
                self.padmux_handle.SysappPadmuxTestScence.DUALOS)
            if ret is False:
                logger.error("prepare_for_test_environment fail.")
                err_code = EC.FAIL
                return err_code

            ret = self.padmux_handle.test_flow_for_bootbin(
                self.padmux_handle.SysappPadmuxTestScence.DUALOS)
            if ret is False:
                logger.error("test_flow_for_bootbin fail.")
                err_code = EC.FAIL
                self.flag_judge_bootbin = False

            ret, info_err = self.padmux_handle.test_flow_for_rtos(
                self.padmux_handle.SysappPadmuxTestMode.TESTLIST)
            if ret is False:
                logger.error("test_flow_for_rtos fail. next is error info")
                for info in info_err:
                    logger.warning("----------------------------------------")
                    logger.warning(f"pin index           is {info['pin_index']}")
                    logger.warning(f"pin pin_mode        is {info['pin_mode']}")
                    logger.warning(f"pin pin_mode_name   is {info['pin_mode_name']}")
                    logger.warning("----------------------------------------")
                err_code = EC.FAIL
                self.flag_judge_rtos = False

            # Clear the rtos configuration to prepare for the following kernel test
            ret = self.padmux_handle.replace_rtos_padmux_for_blank()
            if ret is False:
                logger.error("replace_rtos_padmux_for_blank fail.")
                err_code = EC.FAIL
                return err_code

            ret, info_err = self.padmux_handle.test_flow_for_linux(
                self.padmux_handle.SysappPadmuxTestMode.TESTLIST)
            if ret is False:
                logger.error("test_flow_for_linux fail. next is error info")
                for info in info_err:
                    logger.warning("----------------------------------------")
                    logger.warning(f"pin index           is {info['pin_index']}")
                    logger.warning(f"pin pin_mode        is {info['pin_mode']}")
                    logger.warning(f"pin pin_mode_name   is {info['pin_mode_name']}")
                    logger.warning("----------------------------------------")
                err_code = EC.FAIL
                self.flag_judge_kernel = False

            self.judge_fail_result()
            if ret is False:
                logger.error("judge_fail_result fail.")
                err_code = EC.FAIL
                return err_code

        except Exception as e:
            logger.error(f"Exception occurred: {str(e)}")
            err_code = EC.FAIL
        finally:
            ret = self.padmux_handle.restore_for_test_environment(
                self.padmux_handle.SysappPadmuxTestScence.DUALOS)
            if ret is False:
                logger.error(f"{self.case_name} case_deinit fail.")

        return err_code

    @sysapp_print.print_line_info
    def system_help(self):
        """help info
        Args:
            None
        Returns:
            None
        """
        logger.warning("Test Info")
        logger.warning("1.Detects the pin-mode setting behavior of boot.bin in the dualos scenario")
        logger.warning("2.Detects the pin-mode setting behavior of rtos in the dualos scenario")
        logger.warning("3.Detects the pin-mode setting behavior of kernel in the dualos scenario")
        logger.warning("Next Flow Is WHITELIST")
        self.padmux_handle.printf_list_whitelist()
