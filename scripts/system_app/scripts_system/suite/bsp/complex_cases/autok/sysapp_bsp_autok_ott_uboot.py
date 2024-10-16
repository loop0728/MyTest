
"""ott case in uboot scnce"""
from suite.common.sysapp_common_logger import logger, sysapp_print
from suite.common.sysapp_common_reboot_opts import SysappRebootOpts
from suite.common.sysapp_common_case_base import SysappCaseBase as CaseBase
from suite.common.sysapp_common_types import SysappErrorCodes as EC
from suite.bsp.complex_cases.autok.sysapp_bsp_autok_base import SysappBspAutokBase as AutokBase
from sysapp_client import SysappClient


class SysappBspAutokOttUboot(CaseBase):
    """Autok And Ott Nomal Boot Flow Case

    Test Info
    1.OTT Run Flow Whether it is normal under empty boot
    2.OTT Uboot CMD Run Flow Whether it is normal

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
    def case_deinit_autok(self) -> bool:
        """Case DeInit function

        Args:
            na
        Returns:
            bool: True for success, False fail.
        """
        #result = sys_common.goto_kernel(self.uart)
        result = SysappRebootOpts.reboot_to_kernel(self.uart)
        if result is False:
            logger.error("case_deinit_autok Fail")

        logger.info("run case_deinit_autok succeed")
        return True

    @sysapp_print.print_line_info
    def _case_init_autok(self) -> bool:
        """Case DeInit function

        Args:
            NA
        Returns:
            bool: True for success, False fail.
        """
        ret = self.autok_handle.reboot_in_uboot()
        if ret is False:
            logger.error("Go to Uboot fail.")
            return False

        ret = self.autok_handle.flash_erase()
        if ret is False:
            logger.error("flash_erase fail.")
            return False

        ret = self.autok_handle.reboot_in_uboot()
        if ret is False:
            logger.error("Go to Uboot fail.")
            return False
        return True

    @sysapp_print.print_line_info
    def judge_force_mode(self) -> bool:
        """Case DeInit function

        Args:
            na
        Returns:
            bool: True for success, False fail.
        """
        ret = self.autok_handle.judge_force_flag_flow(self.autok_handle.SysappOttFlag.FORCE_AUTOK)
        if ret is False:
            logger.error("judge_force_autok_flow fail.")
            return False

        ret = self.autok_handle.judge_force_flag_flow(self.autok_handle.SysappOttFlag.FORCE_OTT)
        if ret is False:
            logger.error("judge_force_ott_flow fail.")
            return False
        return True

    @sysapp_print.print_line_info
    def judge_force_autok_ott(self) -> bool:
        """Case DeInit function

        Args:
            na
        Returns:
            bool: True for success, False fail.
        """
        ret = self.autok_handle.judge_flow_autok_ott(self.autok_handle.SysappDdrTrainFlow.AUTOK,
                                                     "uboot")
        if ret is False:
            logger.error("judge_flow_autok fail.")
            return False

        ret = self.autok_handle.reboot_in_uboot()
        if ret is False:
            logger.error("Go to Uboot fail.")
            return False

        ret = self.autok_handle.judge_flow_autok_ott(self.autok_handle.SysappDdrTrainFlow.OTT,
                                                     "uboot")
        if ret is False:
            logger.error("judge_flow_ott fail.")
            return False
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
        ret = self._case_init_autok()
        if ret is False:
            logger.error("case_init_autok fail.")
            err_code = EC.FAIL
            return err_code

        ret = self.autok_handle.judge_ubootcmd_ott_flag(self.autok_handle.SysappOttFlag.FORCE_OTT)
        if ret is False:
            logger.error("judge_ubootcmd_ott_flag fail.")
            err_code = EC.FAIL
            return err_code

        ret = self.judge_force_autok_ott()
        if ret is False:
            logger.error("judge_force_autok_ott fail")
            err_code = EC.FAIL
            return err_code

        ret = self.judge_force_mode()
        if ret is False:
            logger.error(f"{self.case_name} judge_force_mode fail.")
            err_code = EC.FAIL
            return err_code

        ret = self.case_deinit_autok()
        if ret is False:
            logger.error("Go to Uboot fail.")
            err_code = EC.FAIL
            return err_code

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
        logger.warning("1.OTT Run Flow Whether it is normal under empty boot")
        logger.warning("2.OTT Uboot CMD Run Flow Whether it is normal")
