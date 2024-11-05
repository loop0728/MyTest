"""only autok case in nomal flow"""
from suite.common.sysapp_common_logger import logger, sysapp_print
from suite.common.sysapp_common_reboot_opts import SysappRebootOpts
from suite.common.sysapp_common_case_base import SysappCaseBase as CaseBase
from suite.common.sysapp_common_types import SysappErrorCodes as EC
from suite.bsp.complex_cases.autok.sysapp_bsp_autok_base import SysappBspAutokBase as AutokBase
from sysapp_client import SysappClient


class SysappBspAutokOttKernel(CaseBase):
    """Autok And Ott Nomal Boot Flow Case

    Test Info
    1.OTT Run Flow Whether it is normal

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
        self.script_path = script_path
        self.uart = SysappClient(self.case_name, "uart", "uart")
        self.autok_handle = AutokBase(self.uart)
        logger.info(f"{self.case_name} init successful")

    @sysapp_print.print_line_info
    def case_deinit(self):
        """Case DeInit function

        Args:
            na
        """
        #result = sys_common.goto_kernel(self.uart)
        result = SysappRebootOpts.reboot_to_kernel(self.uart)
        if result is False:
            logger.error("case_deinit Fail")

        logger.info("run case_deinit succeed")
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
        try:
            ret = SysappRebootOpts.reboot_to_kernel(self.uart)
            if ret is False:
                logger.error("reboot_in_kernel fail.")
                err_code = EC.FAIL
                return err_code

            ret = self.autok_handle.flash_erase_kernel()
            if ret is False:
                logger.error("flash_erase_kernel fail.")
                err_code = EC.FAIL
                return err_code

            ret = self.autok_handle.judge_flow_autok_ott(
                self.autok_handle.SysappDdrTrainFlow.AUTOK, "linux")
            if ret is False:
                logger.error("judge_flow_autok fail.")
                err_code = EC.FAIL
                return err_code

            ret = self.autok_handle.judge_flow_autok_ott(
                self.autok_handle.SysappDdrTrainFlow.OTT, "linux")
            if ret is False:
                logger.error("judge_flow_autok fail.")
                err_code = EC.FAIL
                return err_code
        except Exception as e:
            logger.error(f"Exception occurred: {str(e)}")
            err_code = EC.FAIL
        finally:
            ret = self.case_deinit()
            if ret is False:
                logger.error(f"{self.case_name} case_deinit fail.")

        return err_code

    @sysapp_print.print_line_info
    @staticmethod
    def system_help():
        """help info
        Args:
            None
        Returns:
            None
        """
        logger.warning("OTT Run Flow Whether it is normal")
