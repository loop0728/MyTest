"""autok and ott case base"""
import time
import re
from enum import Enum
import suite.common.sysapp_common_utils as SysappUtils
from suite.common.sysapp_common_logger import logger, sysapp_print
from suite.common.sysapp_common_reboot_opts import SysappRebootOpts
# from suite.common.sysapp_common_register_opts import SysappRegisterOpts
from cases.platform.bsp.complex_cases.autok.sysapp_bsp_autok_base_var import (BOOTING_TIME_STANDARD,
                                            OTT_FORCE_FLAG,OTT_MODE_UBOOT_KEYWORD, OTT_MODE_REG,
                                            OTT_CMD_UBOOT, OTT_PARTITION_NAME)

class SysappBspAutokBase():
    """Autok Nomal Boot Flow Case

    Test Info
    1.Autok And Ott Test case base class

    Attributes:
            case_uart (handle): case uart handle
    """
    def __init__(self, case_uart):
        """Case Init function

        Args:
            case_uart: uart conlse
            ott_time_standard: ott_time_standard in booting time (us)
            autok_time_standard: autok_time_standard in booting time (us)
        """
        # super().__init__(case_name="s", case_run_cnt=1, script_path='/')
        self.uart = case_uart
        self.ott_time_standard = BOOTING_TIME_STANDARD["OTT_TIME_STANDARD"]
        self.autok_time_standard = BOOTING_TIME_STANDARD["AUTOK_TIME_STANDARD"]
        logger.info("SysappBspAutokBase init successful")

    class SysappDdrTrainFlow(Enum):
        """Ott Partition Flag Enum"""
        OTT = 0
        AUTOK = 1

    class SysappOttFlag(Enum):
        """Ott Partition Flag Enum"""
        FORCE_OTT = OTT_FORCE_FLAG["OTT_FLAG"]
        FORCE_AUTOK = OTT_FORCE_FLAG["AUTOK_FLAG"]

    class SysappOttMode(Enum):
        """Ott And Autok Run Stage Enum"""
        USE_DEFULT = OTT_MODE_UBOOT_KEYWORD["USE_DEFUL"]
        USE_TRAIN_DATA = OTT_MODE_UBOOT_KEYWORD["USE_TRAIN_DATA"]
        RUN_AUTOK = OTT_MODE_UBOOT_KEYWORD["RUN_AUTOK"]

    @sysapp_print.print_line_info
    def judge_ubootcmd_ott_flag(self, target_flag) -> bool:
        """Determine whether to OTT flag or autok Flow by ddr_ott dump cmd

        Args:
            target_flag (enum): FORCE_OTT Or FORCE_AUTOK

        Returns:
            bool: True for success, False fail.
        """
        ss_input = OTT_CMD_UBOOT["DUMP"]
        keyword = "flag:"
        wait_line = 50
        result, data = SysappUtils.write_and_match_keyword(
            self.uart, ss_input, keyword, wait_line)
        if result is True:
            if target_flag.value in data:
                logger.info(f"OTT Flag is {target_flag},match OK")
            else:
                logger.error(
                    f"OTT Flag is {target_flag.value},data is {data},match Fail")
                return False
        else:
            logger.error(f"{ss_input} run fail")
            return False

        logger.info(f"run judge_ubootcmd_ott_flag {target_flag}")
        return True

    @sysapp_print.print_line_info
    def set_ubootcmd_ott_flag(self, target_flag) -> bool:
        """set ott flag by ddr_ott force <0|1> cmd

        Args:
            target_flag (enum): FORCE_OTT Or FORCE_AUTOK

        Returns:
            bool: True for set success, False set fail.
        """
        if self.SysappOttFlag.FORCE_OTT == target_flag:
            ss_input = OTT_CMD_UBOOT["FORCE_OTT"]
        elif self.SysappOttFlag.FORCE_AUTOK == target_flag:
            ss_input = OTT_CMD_UBOOT["FORCE_AUTOK"]
        else:
            logger.error(
                f"set_ubootcmd_ott_flag parm {target_flag} Fail")
            return False
        keyword = "complete"
        wait_line = 50
        result, _ = SysappUtils.write_and_match_keyword(
            self.uart, ss_input, keyword, wait_line)
        if result is True:
            logger.info(f"OTT Flag {ss_input} Set OK")
        else:
            logger.error(f"{ss_input} run fail keyword is {keyword}")
            return False
        logger.info(f"run set_ubootcmd_ott_flag {target_flag}")
        return True

    @sysapp_print.print_line_info
    def judge_ubootcmd_ott_mode(self, target_mode) -> bool:
        """judge ott mode by ddr_ott mode cmd

        Args:
            target_mode (enum): USE_DEFULT or USE_TRAIN_DATA or RUN_AUTOK

        Returns:
            bool: True for judge success, False judge fail.
        """
        keyword = ""
        logger.info(f"run judge_ubootcmd_ott_mode {target_mode}")
        if self.SysappOttMode.USE_DEFULT == target_mode:
            keyword = OTT_MODE_UBOOT_KEYWORD["USE_DEFUL"]
        elif self.SysappOttMode.USE_TRAIN_DATA == target_mode:
            keyword = OTT_MODE_UBOOT_KEYWORD["USE_TRAIN_DATA"]
        elif self.SysappOttMode.RUN_AUTOK == target_mode:
            keyword = OTT_MODE_UBOOT_KEYWORD["RUN_AUTOK"]
        else:
            logger.error(
                f"judge_ubootcmd_ott_mode {target_mode} parm fail")
            return False
        logger.info(f"Ott keyword is {keyword}")
        ss_input = OTT_CMD_UBOOT["MODE"]
        wait_line = 2
        result, _ = SysappUtils.write_and_match_keyword(
            self.uart, ss_input, keyword, wait_line)
        if result is True:
            logger.info(f"cmd {ss_input} run ok")
        else:
            logger.error(f"cmd {ss_input} run fail keyword is {keyword}, data is {_}")
            return False

        logger.info("run judge_ubootcmd_ott_mode ok")
        return True

    @sysapp_print.print_line_info
    def judge_ubootreg_ott_mode(self, target_mode) -> bool:
        """judge ott mode by ott mode register

        Args:
            target_mode (enum): USE_DEFULT or USE_TRAIN_DATA or RUN_AUTOK

        Returns:
            bool: True for judge success, False judge fail.
        """
        keyword = ""
        # str_reg_value = ""
        logger.info(f"run judge_ubootreg_ott_mode {target_mode}")
        if self.SysappOttMode.USE_DEFULT == target_mode:
            keyword = OTT_MODE_REG["USE_DEFUL"]
        elif self.SysappOttMode.USE_TRAIN_DATA == target_mode:
            keyword = OTT_MODE_REG["USE_TRAIN_DATA"]
        elif self.SysappOttMode.RUN_AUTOK == target_mode:
            keyword = OTT_MODE_REG["RUN_AUTOK"]
        else:
            logger.error(
                f"judge_ubootreg_ott_mode {target_mode} parm fail")
            return False
        logger.info(f"Ott keyword is {keyword}")

        # result, str_reg_value = SysappRegisterOpts.read_register(self.uart, OTT_MODE_REG['BANK'],
        #                                                          OTT_MODE_REG['OFFSET'])
        # if result is True:
        #     if str_reg_value == keyword:
        #         logger.error(f"read reg {OTT_MODE_REG['BANK']} {OTT_MODE_REG['OFFSET']} fail,\
        #                      keyword is {keyword},str_reg_value is {str_reg_value}")
        #         return False
        # else:
        #     logger.error("read_register fail!")
        #     return False
        ss_input = f"riu_r {OTT_MODE_REG['BANK']} {OTT_MODE_REG['OFFSET']}"
        wait_line = 10
        result, _ = SysappUtils.write_and_match_keyword(
            self.uart, ss_input, keyword, wait_line)
        if result is True:
            logger.info(f"cmd {ss_input} run ok")
        else:
            logger.error(f"cmd {ss_input} run fail keyword is {keyword},data is {_}")
            return False

        logger.info("run judge_ubootreg_ott_mode pass")
        return True

    @sysapp_print.print_line_info
    def set_kernelreg_autok_mode(self, target_mode) -> bool:
        """set auok mode by /customer/riu_w in kernel

        Args:
            target_mode (enum): USE_DEFULT or USE_TRAIN_DATA or RUN_AUTOK

        Returns:
            bool: True for set OK, False set fail.
        """
        keyword = ""
        logger.info(f"run set_kernelreg_autok_mode {target_mode}")
        if self.SysappOttMode.USE_DEFULT == target_mode:
            ss_input = f"/customer/riu_w {OTT_MODE_REG['BANK']} {OTT_MODE_REG['OFFSET']} \
                {OTT_MODE_REG['USE_DEFUL']}"
            keyword = OTT_MODE_REG["USE_DEFUL"]
        elif self.SysappOttMode.USE_TRAIN_DATA == target_mode:
            ss_input = f"/customer/riu_w {OTT_MODE_REG['BANK']} {OTT_MODE_REG['OFFSET']} \
                {OTT_MODE_REG['USE_TRAIN_DATA']}"
            keyword = OTT_MODE_REG["USE_TRAIN_DATA"]
        elif self.SysappOttMode.RUN_AUTOK == target_mode:
            ss_input = f"/customer/riu_w {OTT_MODE_REG['BANK']} {OTT_MODE_REG['OFFSET']} \
                {OTT_MODE_REG['RUN_AUTOK']}"
            keyword = OTT_MODE_REG["RUN_AUTOK"]
        else:
            logger.error(
                f"set_kernelreg_autok_mode {target_mode} parm fail")
            return False
        logger.info(f"Ott keyword is {keyword}")
        wait_line = 10
        result, _ = SysappUtils.write_and_match_keyword(
            self.uart, ss_input, keyword, wait_line)
        if result is True:
            logger.info(f"cmd {ss_input} set ok")
        else:
            logger.error(f"cmd {ss_input} set fail,data is {_}")
            return False

        logger.info("run set_kernelreg_autok_mode pass")
        return True

    @sysapp_print.print_line_info
    def judge_kernelreg_autok_mode(self, target_mode) -> bool:
        """judge auok mode by riu_r in kernel

        Args:
            target_mode (enum): USE_DEFULT or USE_TRAIN_DATA or RUN_AUTOK

        Returns:
            bool: True for judge ok, False judge fail.
        """
        keyword = ""
        logger.info(f"run judge_kernelreg_autok_mode {target_mode}")
        if self.SysappOttMode.USE_DEFULT == target_mode:
            keyword = OTT_MODE_REG["USE_DEFUL"]
        elif self.SysappOttMode.USE_TRAIN_DATA == target_mode:
            keyword = OTT_MODE_REG["USE_TRAIN_DATA"]
        elif self.SysappOttMode.RUN_AUTOK == target_mode:
            keyword = OTT_MODE_REG["RUN_AUTOK"]
        else:
            logger.error(
                f"judge_kernelreg_autok_mode {target_mode} parm fail")
            return False
        logger.info(f"Ott keyword is {keyword}")
        ss_input = f"/customer/riu_r {OTT_MODE_REG['BANK']} {OTT_MODE_REG['OFFSET']}"
        wait_line = 10
        result, data = SysappUtils.write_and_match_keyword(
            self.uart, ss_input, keyword, wait_line)

        if result is True:
            logger.info(f"cmd {ss_input} judge ok")
        else:
            logger.error(f"cmd {ss_input} judge fail,data is {data}")
            return False
        logger.info("run judge_kernelreg_autok_mode pass")
        return True

    @sysapp_print.print_line_info
    def run_scene_str(self, alarm_time) -> bool:
        """run str and auto resume

        Args:
            alarm_time: set str auto resume time

        Returns:
            bool: True run str ok, False run str fail.
        """
        ss_input = "ls /sys/devices/virtual/sstar/rtcpwc/alarm_timer"
        keyword = "/sys/devices/virtual/sstar/rtcpwc/alarm_timer"
        wait_line = 2
        result, _ = SysappUtils.write_and_match_keyword(
            self.uart, ss_input, keyword, wait_line)
        if result is True:
            logger.info(f"cmd {ss_input} run ok")
        else:
            logger.error(f"cmd {ss_input} run fail,data is {_}")
            return False

        ss_input = f"echo {alarm_time} > /sys/devices/virtual/sstar/rtcpwc/alarm_timer"
        keyword = "#"
        wait_line = 2
        result, _ = SysappUtils.write_and_match_keyword(
            self.uart, ss_input, keyword, wait_line)
        if result is True:
            logger.info(f"cmd {ss_input} run ok")
        else:
            logger.error(f"cmd {ss_input} run fail,data is {_}")
            return False

        ss_input = "echo mem > /sys/power/state"
        result = self.uart.write(ss_input)
        if result is True:
            logger.info(f"cmd {ss_input} run ok")
        else:
            logger.error(f"cmd {ss_input} run fail")
            return False
        # Prevent a long resume time from affecting subsequent log retrieval
        time.sleep(alarm_time + 4)

        ss_input = "cat /proc/kmsg &"
        keyword = "PM: suspend exit"
        wait_line = 20000
        result, _ = SysappUtils.write_and_match_keyword(
            self.uart, ss_input, keyword, wait_line)
        if result is True:
            logger.info("resume run ok")
            result = self.uart.write("pkill -f 'cat /proc/kmsg'")
            if result is False:
                logger.error("cmd pkill -f 'cat /proc/kmsg' fail")
                return False
        else:
            logger.error(f"cmd {ss_input},resume fail,data is {_}")
            return False

        logger.info("run run_scene_str pass")
        return True

    @sysapp_print.print_line_info
    def uboot_run_kernel(self) -> bool:
        """run in kernel in uboot

        Args:
            Na

        Returns:
            bool: success in kernel, False fail to kernel.
        """
        ss_input = "ls"
        keyword = "SigmaStar #"
        wait_line = 2
        result, _ = SysappUtils.write_and_match_keyword(
            self.uart, ss_input, keyword, wait_line)
        if result is True:
            ss_input = "run bootcmd"
        else:
            logger.error("Not in Uboot")
            return False
        result = self.uart.write(ss_input)
        if result is False:
            logger.error(f"run {ss_input} fail")
            return False

        # Prevent a long uboot to kerenl time from affecting subsequent log retrieval
        time.sleep(4)

        ss_input = "cd /"
        keyword = "/ #"
        wait_line = 2
        result, _ = SysappUtils.write_and_match_keyword(
            self.uart, ss_input, keyword, wait_line)
        if result is False:
            logger.info(f"uboot run in kernel fail,data is {_}")
            return False
        logger.info("run uboot_run_kernel pass")
        return True

    @sysapp_print.print_line_info
    def reboot_in_uboot(self) -> bool:
        """reboot second in uboot

        Args:
            Na

        Returns:
            bool: success in reboot in boot, False fail to kernel.
        """
        ss_input = "ls"
        keyword = "SigmaStar #"
        wait_line = 2
        result, _ = SysappUtils.write_and_match_keyword(
            self.uart, ss_input, keyword, wait_line)
        if result is True:
            ss_input = "reset"
            logger.info("I'm in the uboot.")
        else:
            ss_input = "reboot -f"
            logger.info("I'm in the kernel.")
        time.sleep(1)
        result = self.uart.write(ss_input)
        if result is True:
            start_time = time.time()
            while time.time() - start_time < 5:
                self.uart.write("")
        else:
            logger.error(f"{ss_input} run fail")
            return False

        ss_input = ""
        keyword = "SigmaStar #"
        wait_line = 2
        result, _ = SysappUtils.write_and_match_keyword(
            self.uart, ss_input, keyword, wait_line)
        if result is True:
            logger.info("I'm in the uboot.")
            return True
        else:
            logger.error("Go to uboot fail.")
            return False

    @sysapp_print.print_line_info
    def judge_bootingtime(self, target_flow) -> bool:
        """Determine whether to go OTT flow or autok Flow by reading kernel bootingtime

        Args:
            target_flow (enum): self.SysappDdrTrainFlow.OTT or self.SysappDdrTrainFlow.AUTOK

        Returns:
            bool: True for judge success, False judge fail.
        """
        time.sleep(1)
        ss_input = "cat /sys/devices/virtual/sstar/msys/booting_time"
        keyword = "001"
        wait_line = 10
        result, data = SysappUtils.write_and_match_keyword(
            self.uart, ss_input, keyword, wait_line)
        if result is True:
            logger.info("booting_time run OK")
            match = re.search(r'diff:\s*(\d+)', data)
            if match:
                time_value_nextflow = int(match.group(1))
                logger.info(
                    f'IPL nextflow Time diff: {time_value_nextflow}')
            else:
                logger.error('IPL booting_time No match found')
                return False
        else:
            logger.error(f"cmd {ss_input} fail,data is {data}")
            return False

        if self.SysappDdrTrainFlow.OTT == target_flow:
            logger.info(f"Ott Time stard is {self.ott_time_standard}")
            if self.ott_time_standard < time_value_nextflow:
                logger.error("Ott Time anomaly")
                return False
        elif self.SysappDdrTrainFlow.AUTOK == target_flow:
            logger.info(
                f"AUTOK Time stard is {self.autok_time_standard}")
            if self.autok_time_standard > time_value_nextflow:
                logger.error("autok Time anomaly")
                return False
        else:
            logger.error(f"judge_bootingtime {target_flow} parm fail")
            return False

        time.sleep(1)
        logger.info(
            f"fun parm is {target_flow},time is {time_value_nextflow}")
        return True

    @sysapp_print.print_line_info
    def _judge_kernel_autok_ott(self, target_flow, target_mode) -> bool:
        """Determine whether to go OTT flow or autok Flow in kernel

        Args:
            target_flow (enum): SysappDdrTrainFlow.AUTOK or SysappDdrTrainFlow.USE_TRAIN_DATA
            target_mode (enum): SysappOttMode.RUN_AUTOK or SysappOttMode.USE_TRAIN_DATA

        Returns:
            bool: True for judge success, False judge fail.
        """
        ret = SysappRebootOpts.reboot_to_kernel(self.uart)
        if ret is False:
            logger.error("reboot_in_kernel fail")
            return False
        ret = self.judge_bootingtime(target_flow)
        if ret is False:
            logger.error("judge_bootingtime fail")
            return False
        ret = self.judge_kernelreg_autok_mode(target_mode)
        if ret is False:
            logger.error("judge_kernelreg_autok_mode fail")
            return False
        return True

    @sysapp_print.print_line_info
    def _judge_uboot_autok_ott(self, target_flow, target_mode) -> bool:
        """Determine whether to go OTT flow or autok Flow int uboot

        Args:
            target_flow (enum): SysappDdrTrainFlow.AUTOK or SysappDdrTrainFlow.USE_TRAIN_DATA
            target_mode (enum): SysappOttMode.RUN_AUTOK or SysappOttMode.USE_TRAIN_DATA

        Returns:
            bool: True for judge success, False judge fail.
        """
        ret = self.judge_ubootcmd_ott_mode(target_mode)
        if ret is False:
            logger.error("judge_ubootcmd_ott_mode fail")
            return False
        ret = self.judge_ubootreg_ott_mode(target_mode)
        if ret is False:
            logger.error("judge_ubootreg_ott_mode fail")
            return False
        ret = self.uboot_run_kernel()
        if ret is False:
            logger.error("uboot_run_kernel fail")
            return False
        ret = self.judge_bootingtime(target_flow)
        if ret is False:
            logger.error("judge_bootingtime fail")
            return False
        ret = self.judge_kernelreg_autok_mode(target_mode)
        if ret is False:
            logger.error("judge_kernelreg_autok_mode fail")
            return False
        return True

    @sysapp_print.print_line_info
    def judge_flow_autok_ott(self, target_flow, target_os) -> bool:
        """Determine whether to go OTT flow or autok Flow

        Args:
            target_flow (enum): SysappDdrTrainFlow.AUTOK or SysappDdrTrainFlow.USE_TRAIN_DATA
            target_os: "linux" or "uboot"

        Returns:
            bool: True for judge success, False judge fail.
        """
        logger.info(f"judge_force_flag_flow parm os {target_os} fail")
        if target_flow == self.SysappDdrTrainFlow.AUTOK:
            target_mode = self.SysappOttMode.RUN_AUTOK
        elif target_flow == self.SysappDdrTrainFlow.OTT:
            target_mode = self.SysappOttMode.USE_TRAIN_DATA
        else:
            logger.error(
                f"judge_force_flag_flow target_flow parm {target_flow} fail")
            return False

        if target_os == "linux":
            ret = self._judge_kernel_autok_ott(target_flow, target_mode)
            if ret is False:
                logger.error("_judge_kernel_autok_ott fail")
                return False
        elif target_os == "uboot":
            ret = self._judge_uboot_autok_ott(target_flow, target_mode)
            if ret is False:
                logger.error("_judge_uboot_autok_ott fail")
                return False
        else:
            logger.error(f"judge_force_flag_flow target_os parm {target_os} fail")
            return False

        logger.info("judge_force_flag_flow parm os pass")
        return True

    @sysapp_print.print_line_info
    def _judge_ubootcmd(self, target_flag) -> bool:
        """Determine whether to judge OTT flow by Uboot Cmd

        Args:
            target_flag (enum):  SysappOttFlag.FORCE_OTT or  SysappOttFlag.FORCE_AUTOK

        Returns:
            bool: True for judge success, False judge fail.
        """
        ret = self.reboot_in_uboot()
        if ret is False:
            logger.error("reboot_in_uboot fail")
            return False
        ret = self.judge_ubootcmd_ott_flag(target_flag)
        if ret is False:
            logger.error("judge_ubootcmd_ott_flag fail")
            return False
        ret = self.judge_ubootcmd_ott_mode(self.SysappOttMode.RUN_AUTOK)
        if ret is False:
            logger.error("judge_bootingtime fail")
            return False
        ret = self.judge_ubootreg_ott_mode(self.SysappOttMode.RUN_AUTOK)
        if ret is False:
            logger.error("judge_ubootreg_ott_mode fail")
            return False
        return True

    @sysapp_print.print_line_info
    def _uboot_force_flag_flow(self, target_flag) -> bool:
        """Determine whether to OTT flow For force mode in uboot

        Args:
            target_flag (enum):  SysappOttFlag.FORCE_OTT or  SysappOttFlag.FORCE_AUTOK

        Returns:
            bool: True for success, False fail.
        """
        ret = self.reboot_in_uboot()
        if ret is False:
            logger.error("reboot_in_uboot fail")
            return False
        ret = self.set_ubootcmd_ott_flag(target_flag)
        if ret is False:
            logger.error("set_ubootcmd_ott_flag fail")
            return False
        ret = self._judge_ubootcmd(target_flag)
        if ret is False:
            logger.error("_judge_ubootcmd fail")
            return False
        return True

    @sysapp_print.print_line_info
    def _uboot_force_flag_flow_special_autok(self) -> bool:
        """Determine whether to OTT flow For force mode in uboot but special for Ott

        Args:
            Na

        Returns:
            bool: True for success, False fail.
        """
        ret = self.reboot_in_uboot()
        if ret is False:
            logger.error("reboot_in_uboot fail")
            return False
        ret = self.judge_ubootcmd_ott_mode(
                self.SysappOttMode.USE_TRAIN_DATA),
        if ret is False:
            logger.error("judge_ubootcmd_ott_mode fail")
            return False
        ret = self.judge_ubootreg_ott_mode(
                self.SysappOttMode.USE_TRAIN_DATA)
        if ret is False:
            logger.error("judge_ubootreg_ott_mode fail")
            return False
        return True

    @sysapp_print.print_line_info
    def _judge_kernel_booting(self, target_flow) -> bool:
        """Determine whether to go OTT flow or autok Flow by reading bootingtime

        Args:
            target_flow (enum): self.SysappDdrTrainFlow.OTT or self.SysappDdrTrainFlow.AUTOK

        Returns:
            bool: True for success, False fail.
        """
        ret = self.uboot_run_kernel()
        if ret is False:
            logger.error("uboot_run_kernel fail")
            return False
        ret = self.judge_bootingtime(target_flow)
        if ret is False:
            logger.error("judge_kernelreg_autok_mode")
            return False
        return True

    @sysapp_print.print_line_info
    def _ott_judge_force_flow(self, target_flag, target_flow) -> bool:
        """Determine whether to go OTT flow For Force Flow

        Args:
            target_flag (enum):  SysappOttFlag.FORCE_OTT or  SysappOttFlag.FORCE_AUTOK
            target_flow (enum): self.SysappDdrTrainFlow.OTT or self.SysappDdrTrainFlow.AUTOK
        Returns:
            bool: True for success, False fail.
        """
        ret = self._uboot_force_flag_flow(target_flag)
        if ret is False:
            logger.error("_uboot_force_flag_flow fail")
            return False
        ret = self._uboot_force_flag_flow_special_autok()
        if ret is False:
            logger.error("_uboot_force_flag_flow_special_autok fail")
            return False
        ret = self._judge_kernel_booting(target_flow)
        if ret is False:
            logger.error("_judge_kernel_booting fail")
            return False
        return True

    @sysapp_print.print_line_info
    def judge_force_flag_flow(self, target_flag) -> bool:
        """Determine whether to go OTT flow or autok Flow

        Args:
            target_flag (enum):  SysappOttFlag.FORCE_OTT or  SysappOttFlag.FORCE_AUTOK

        Returns:
            bool: True for success, False fail.
        """
        if self.SysappOttFlag.FORCE_OTT == target_flag:
            target_flow = self.SysappDdrTrainFlow.OTT
            ret = self._ott_judge_force_flow(target_flag, target_flow)
            if ret is False:
                logger.error("_ott_judge_force_flow fail")
                return False
        elif self.SysappOttFlag.FORCE_AUTOK == target_flag:
            target_flow = self.SysappDdrTrainFlow.AUTOK
            ret = self._uboot_force_flag_flow(target_flag)
            if ret is False:
                logger.error("_uboot_force_flag_flow fail")
                return False
            ret = self._judge_kernel_booting(target_flow)
            if ret is False:
                logger.error("_judge_kernel_booting fail")
                return False
        else:
            logger.error(f"judge_force_flag_flow parm {target_flag} fail")
            return False
        logger.info("run judge_force_flag_flow pass")
        return True

    @sysapp_print.print_line_info
    def flash_erase(self) -> bool:
        """Determine whether to go OTT flow or autok Flow by reading bootingtime

        Args:
            target_flow (enum): ott or autok

        Returns:
            bool: True for success, False fail.
        """
        self.uart.write(f"nand erase.part {OTT_PARTITION_NAME}")
        logger.info("run flash_erase pass")
        return True

    @sysapp_print.print_line_info
    def flash_erase_kernel(self) -> bool:
        """Determine whether to go OTT flow or autok Flow by reading bootingtime

        Args:
            target_flow (enum): ott or autok

        Returns:
            bool: True for success, False fail.
        """
        ss_input = "cat /proc/mtd"
        keyword = OTT_PARTITION_NAME
        wait_line = 100
        result, data = SysappUtils.write_and_match_keyword(
            self.uart, ss_input, keyword, wait_line)
        if result is True:
            logger.info("find partition OK")
            str_mtd = data.split(':')[0].strip()
            if str_mtd:
                logger.info(f'ott partiton mtd is {str_mtd}')
                self.uart.write(f"flash_eraseall /dev/{str_mtd}")
                time.sleep(6)
            else:
                logger.error('ott partiton mtd No match, data is {data}')
                return False
        else:
            logger.error(f"cmd {ss_input} fail.")
            return False

        logger.info("run flash_erase_kernel pass")
        return True
