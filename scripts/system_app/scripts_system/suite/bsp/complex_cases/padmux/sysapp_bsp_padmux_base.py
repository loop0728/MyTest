"""autok and ott case base"""
import time
from enum import Enum
import suite.common.sysapp_common_utils as SysappUtils
from suite.common.sysapp_common_logger import logger, sysapp_print
from suite.common.sysapp_common_net_opts import SysappNetOpts
from suite.common.sysapp_common_reboot_opts import SysappRebootOpts
from suite.bsp.common.sysapp_bsp_dts_ops import SysappBspDtsOps as BspDtsOps
from suite.bsp.common.sysapp_bsp_storage import SysappBspStorage as BspStorage
from cases.platform.bsp.complex_cases.padmux.sysapp_bsp_padmux_base_var import (
    TEST_LIST_PIN_MODE, TEST_WHITELIST_PIN_MOD, TOOL_IO_CHECK)


class SysappBspPadmuxBase():
    """Test Padmux Case

    Test Info
    1.Padmux in Purelinux and Dualos Scence case base class

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
        self.replace_storage = BspStorage(self.uart)
        self.replace_base = BspDtsOps(self.uart, self.replace_storage)
        self.list_replace_rtos = []
        self.list_replace_kernel = ""
        self.list_pin_mode = TEST_LIST_PIN_MODE
        self.list_whitelist_pin_mode = TEST_WHITELIST_PIN_MOD
        logger.info("SysappBspPadmuxBase init successful")

    class SysappPadmuxTestMode(Enum):
        """Change the dts mode"""
        BLANK = "Change the padmux to blank"
        TESTLIST = "Change the padmux to testlist"

    class SysappPadmuxTestScence(Enum):
        """Test scenario"""
        PURELINUX = 0
        DUALOS = 1

    @sysapp_print.print_line_info
    def mount_environment(self) -> bool:
        """Mount Environment setup before running case

        Args:
            Na

        Returns:
            bool: True for success, False fail.
        """
        result = False
        result = SysappNetOpts.setup_network(self.uart)
        if result is False:
            logger.error("setup_network failed")
            return False

        result = SysappNetOpts.mount_server_path_to_board(self.uart, "")
        if result is False:
            logger.error("mount_server_path_to_board failed")
            return False

        logger.info("run mount_environment ok")
        return True

    @sysapp_print.print_line_info
    def prepare_for_resource(self) -> bool:
        """Environment resource prepare before running case

        Args:
            Na

        Returns:
            bool: True for success, False fail.
        """
        ss_input = ""
        result = False

        result = SysappRebootOpts.reboot_to_kernel(self.uart)
        if result is False:
            logger.error("reboot_in_kernel fail.")
            return result

        result = self.mount_environment()
        if result is False:
            logger.error("mount_environment fail.")
            return result

        # Check the io_check tool
        ss_input = f"ls {TOOL_IO_CHECK}"
        keyword = TOOL_IO_CHECK
        wait_line = 2
        result, data = SysappUtils.write_and_match_keyword(
            self.uart, ss_input, keyword, wait_line)
        print(data + "renpp")
        if result is True:
            if "No such file or directory" in data:
                logger.error(f"iocheck tool not find,cmd is {ss_input},keyword is {keyword},\
                             data is {data}")
                return False
        else:
            logger.error(f"iocheck tool cmd not find,cmd is {ss_input},keyword is{keyword}")
            return False

        logger.info("run prepare_for_resource ok")
        return True

    @sysapp_print.print_line_info
    def prepare_for_test_environment(self, target_scence) -> bool:
        """Environment setup before running case

        Args:
            Na

        Returns:
            bool: True for success, False fail.
        """
        result = False
        temp_arry = []
        temp_str = ""

        result = self.prepare_for_resource()
        if result is False:
            logger.error("run prepare_for_resource fail")
            return result

        # The test environment contains multiple dts changes to facilitate restore
        result = self.replace_base.bsp_dts_get_image("KERNEL")
        if result is False:
            logger.error("KERNEL bsp_dts_get_image fail.")
            return result

        # Create an array for the kernel to replace dts
        for item in self.list_pin_mode:
            temp_str = (
                f"{temp_str} "
                f"{hex(item['pin_index'])} "
                f"{hex(item['pin_mode'])} "
                f"{hex(item['pin_mdrv'])}"
            )
        self.list_replace_kernel = temp_str.strip()
        logger.info(self.list_replace_kernel)

        if target_scence == self.SysappPadmuxTestScence.PURELINUX:
            logger.info(f"target_scence is {target_scence}")
        elif target_scence == self.SysappPadmuxTestScence.DUALOS:
            for item in self.list_pin_mode:
                # Create an array for the rtos to replace sys
                temp_arry.append(
                    f"{hex(item['pin_index'])} {hex(item['pin_mode'])} {hex(item['pin_mdrv'])}")
            self.list_replace_rtos = temp_arry
            logger.info(self.list_replace_rtos)

            result = self.replace_rtos_padmux_for_blank()
            if result is False:
                logger.error("replace_rtos_padmux_for_blank failed")
                return False
            result = self.replace_kernel_padmux_for_blank()
            if result is False:
                logger.error("replace_kernel_padmux_for_blank failed")
                return False
        else:
            logger.error(f"args error target_scence is {target_scence}")
        logger.info("run prepare_for_test_environment ok")
        return True

    @sysapp_print.print_line_info
    def restore_for_test_environment(self, target_scence) -> bool:
        """restore Environment after running case

        Args:
            Na

        Returns:
            bool: True for success, False fail.
        """
        result = False

        result = self.replace_base.image_restore("KERNEL")
        if result is False:
            logger.error("KERNEL image_restore fail.")
            return result

        if target_scence == self.SysappPadmuxTestScence.PURELINUX:
            logger.info(f"target_scence is {target_scence}")
        elif target_scence == self.SysappPadmuxTestScence.DUALOS:
            logger.info("The rtos is not restored")
        else:
            logger.error(f"args error target_scence is {target_scence}")

        logger.info("run restore_for_test_environment ok")
        return True

    @sysapp_print.print_line_info
    def run_io_check_for_test_pin(self, item_list, list_fail_arry) -> bool:
        """Check that the pin-mode list of the test meets the required Settings

        Args:
            Na

        Returns:
            bool: True for judge success, False judge fail.
            dictionary: If False, the data of the false list
        """
        ss_input = ""
        flag_whitelist = False
        data = []
        time.sleep(0.7)
        ss_input = f"{TOOL_IO_CHECK} {item_list['pin_index']}"
        keyword = "This Pin Mode"
        wait_line = 40
        result, data = SysappUtils.write_and_match_keyword(
            self.uart, ss_input, keyword, False, wait_line)
        if result is True:
            if item_list['pin_mode_name'] not in data:
                flag_whitelist = False
                logger.warning(f"pin {item_list['pin_index']} do not patch list")
                for item_whitelist in self.list_whitelist_pin_mode:
                    if item_whitelist['pin_index'] == item_list['pin_index']:
                        if item_whitelist['pin_mode_name'] in data:
                            logger.info(f"pin {item_list['pin_mode_name']} in whitelist")
                        else:
                            logger.error(f"pin {item_list['pin_mode_name']} does not meet \
                                            of the whitelist")
                            list_fail_arry.append(item_list)
                        flag_whitelist = True
                        break
                if flag_whitelist is False:
                    logger.error(f"pin {item_list['pin_index']} does in whitelist")
                    list_fail_arry.append(item_list)
            else:
                logger.info(f"pin {item_list['pin_mode_name']} test OK")
        else:
            logger.error(f"cmd {ss_input} run fail")
            list_fail_arry.append(item_list)
            return False

        return True, list_fail_arry

    @sysapp_print.print_line_info
    def inspect_test_list_pinmode(self) -> bool:
        """Check that the pin-mode list of the test meets the required Settings

        Args:
            Na

        Returns:
            bool: True for judge success, False judge fail.
            dictionary: If False, the data of the false list
        """
        list_fail_arry = []

        for item_list in self.list_pin_mode:
            result = self.run_io_check_for_test_pin(item_list, list_fail_arry)
            if (result is False) or (list_fail_arry != []):
                logger.error("run_io_check_for_pin_mode fail.")
                return result, list_fail_arry

        logger.info("run inspect_test_list_pinmode ok")
        return True, list_fail_arry

    @sysapp_print.print_line_info
    def run_io_check_for_blank_pin(self, item_list, list_fail_arry) -> bool:
        """Check that the pin-mode list of the blank meets the required Settings

        Args:
            Na

        Returns:
            bool: True for judge success, False judge fail.
            dictionary: If False, the data of the false list
        """
        ss_input = ""
        flag_whitelist = False
        data = []
        time.sleep(0.7)
        ss_input = f"{TOOL_IO_CHECK} {item_list['pin_index']}"
        keyword = "This Pin Mode"
        wait_line = 30
        result, data = SysappUtils.write_and_match_keyword(
            self.uart, ss_input, keyword, False, wait_line)
        if result is True:
            if "This Pin Mode Not Set" not in data:
                logger.warning(f"pin {item_list['pin_index']} does not meet the \
                            expectations of theblank")
                for item_whitelist in self.list_whitelist_pin_mode:
                    if item_whitelist['pin_index'] == item_list['pin_index']:
                        if item_whitelist['pin_mode_name'] in data:
                            logger.info(f"pin {item_list['pin_mode_name']} in whitelist")
                        else:
                            logger.error(f"pin {item_list['pin_mode_name']} does not meet \
                                            of the whitelist")
                            list_fail_arry.append(item_list)
                        flag_whitelist = True
                        break
                if flag_whitelist is False:
                    logger.error(f"pin {item_list['pin_index']} does in whitelist")
                    list_fail_arry.append(item_list)
        else:
            logger.error(f"cmd {ss_input} run fail")
            list_fail_arry.append(item_list)
            return False, list_fail_arry
        return True, list_fail_arry

    @sysapp_print.print_line_info
    def inspect_blank_pinmode(self) -> bool:
        """Check that the blank pin-mode list matches the required Settings

        Args:
            Na

        Returns:
            bool: True for judge success, False judge fail
            dictionary: If False, the data of the fail list
        """
        list_fail_arry = []
        result = False

        for item_list in self.list_pin_mode:
            result = self.run_io_check_for_blank_pin(item_list, list_fail_arry)
            if (result is False) or (list_fail_arry != []):
                logger.error("run_io_check_for_pin_mode fail.")
                return result, list_fail_arry

        logger.info("run inspect_blank_pinmode pass")
        return True, list_fail_arry

    @sysapp_print.print_line_info
    def replace_kernel_padmux_for_blank(self) -> bool:
        """Change the padmux in dts in kernel to blank

        Args:
            Na

        Returns:
            bool: True for set OK, False set fail.
        """
        result = False

        result = self.replace_base.delete_dts_lvalue("padmux", "schematic")
        if result is False:
            logger.error("KERNEL delete_dts_lvalue fail.")
            return result
        result = self.replace_base.bsp_dts_genarate_image("kernel")
        if result is False:
            logger.error("KERNEL bsp_dts_genarate_image fail.")
            return result
        result = self.replace_base.bsp_dts_ota_pack("KERNEL")
        if result is False:
            logger.error("KERNEL bsp_dts_ota_pack fail.")
            return result
        result = self.replace_base.bsp_dts_ota_upgrade("KERNEL")
        if result is False:
            logger.error("KERNEL bsp_dts_ota_upgrade fail.")
            return result
        result = self.mount_environment()
        if result is False:
            logger.error("mount_environment fail.")
            return result
        logger.info("run replace_kernel_padmux_for_blank pass")
        return True

    @sysapp_print.print_line_info
    def replace_kernel_padmux_for_testlist(self) -> bool:
        """Change the padmux in dts in kernel to testlist

        Args:
            Na

        Returns:
            bool: True for judge ok, False judge fail.
        """
        result = False

        result = self.replace_base.add_dts_lvalue("padmux", "schematic", self.list_replace_kernel)
        if result is False:
            logger.error("KERNEL add_dts_lvalue fail.")
            return result
        result = self.replace_base.bsp_dts_genarate_image("kernel")
        if result is False:
            logger.error("KERNEL bsp_dts_genarate_image fail.")
            return result
        result = self.replace_base.bsp_dts_ota_pack("KERNEL")
        if result is False:
            logger.error("KERNEL bsp_dts_ota_pack fail.")
            return result
        result = self.replace_base.bsp_dts_ota_upgrade("KERNEL")
        if result is False:
            logger.error("KERNEL bsp_dts_ota_upgrade fail.")
            return result
        result = self.mount_environment()
        if result is False:
            logger.error("mount_environment fail.")
            return result

        logger.info("run replace_kernel_padmux_for_testlist pass")
        return True

    @sysapp_print.print_line_info
    def replace_rtos_padmux_for_blank(self) -> bool:
        """Change the padmux in sys in rtos to bank

        Args:
            Na

        Returns:
            bool: True run str ok, False run str fail.
        """
        # 1.更换rtos中的sys中的padmux设置为空
        logger.info(f"run replace_rtos_padmux_for_blank pass {self.list_whitelist_pin_mode}")
        return True

    @sysapp_print.print_line_info
    def replace_rtos_padmux_for_testlist(self) -> bool:
        """Change the padmux in sys in rtos to testlist

        Args:
            Na

        Returns:
            bool: success in kernel, False fail to kernel.
        """
        # 1.使用self.TEST_LIST_PIN_MODE，生成一个可以给replace使用的数组
        # 2.更换rtos中的sys中的padmux设置为testlist
        logger.info(f"run replace_rtos_padmux_for_testlist pass {self.list_whitelist_pin_mode}")
        return True

    @sysapp_print.print_line_info
    def test_flow_for_bootbin(self, target_scence):
        """judge the padmux in diff scence for boot.bin

        Args:
            target_scence (enum): SysappPadmuxTestScence.PURELINUX Or SysappPadmuxTestScence.DUALOS

        Returns:
            bool: success in kernel, False fail to kernel.
            dictionary: If False, the data of the fail list
        """
        result = False
        list_fail_arry = []

        if target_scence == self.SysappPadmuxTestScence.PURELINUX:
            result = self.replace_kernel_padmux_for_blank()
            if result is False:
                logger.error("replace_kernel_padmux_for_blank failed")
                return False, list_fail_arry
        elif target_scence == self.SysappPadmuxTestScence.DUALOS:
            # This clearing was done in prepare
            logger.info(f"target_scence is {target_scence}")
        else:
            logger.error(f"args error target_scence is {target_scence}")

        result, list_fail_arry = self.inspect_blank_pinmode()
        if (result is False) or (list_fail_arry != []):
            logger.error("inspect_blank_pinmode failed")
            return False, list_fail_arry

        logger.info("run test_flow_for_bootbin pass")
        return True, list_fail_arry

    @sysapp_print.print_line_info
    def test_flow_for_rtos(self, target_mode) -> bool:
        """Change the padmux in rtos

        Args:
            target_mode (enum): SysappPadmuxTestMode.BLANK Or SysappPadmuxTestMode.TESTLIST

        Returns:
            bool: success in kernel, False fail to kernel.
            dictionary: If False, the data of the fail list
        """
        list_fail_arry = []
        if target_mode == self.SysappPadmuxTestMode.BLANK:
            result = self.replace_rtos_padmux_for_blank()
            if result is False:
                logger.error("run replace_rtos_padmux_for_blank fail")
                return False, list_fail_arry
            result, list_fail_arry = self.inspect_blank_pinmode()
            if (result is False) or (list_fail_arry != []):
                logger.error("run inspect_blank_pinmode fail")
                return False, list_fail_arry
        elif target_mode == self.SysappPadmuxTestMode.TESTLIST:
            result = self.replace_rtos_padmux_for_testlist()
            if result is False:
                logger.error("run replace_rtos_padmux_for_testlist fail")
                return False, list_fail_arry
            result, list_fail_arry = self.inspect_test_list_pinmode()
            if (result is False) or (list_fail_arry != []):
                logger.error("run inspect_test_list_pinmode fail")
                return False, list_fail_arry
        else:
            logger.error(f"args error target_mode is {target_mode}")

        logger.info("run test_flow_for_rtos pass")
        return True, list_fail_arry

    @sysapp_print.print_line_info
    def test_flow_for_linux(self, target_mode):
        """Change the padmux in kernel

        Args:
            target_mode (enum): SysappPadmuxTestMode.BLANK Or SysappPadmuxTestMode.TESTLIST

        Returns:
            bool: success in kernel, False fail to kernel.
        """
        list_fail_arry = []
        if target_mode == self.SysappPadmuxTestMode.BLANK:
            result = self.replace_kernel_padmux_for_blank()
            if (result is False) or (list_fail_arry != []):
                logger.error("run replace_kernel_padmux_for_blank fail")
                return False, list_fail_arry
            result, list_fail_arry = self.inspect_blank_pinmode()
            if result is False:
                logger.error("run inspect_blank_pinmode fail")
                return False, list_fail_arry
        elif target_mode == self.SysappPadmuxTestMode.TESTLIST:
            result = self.replace_kernel_padmux_for_testlist()
            if result is False:
                logger.error("run replace_kernel_padmux_for_testlist fail")
                return False, list_fail_arry
            result, list_fail_arry = self.inspect_test_list_pinmode()
            if (result is False) or (list_fail_arry != []):
                logger.error("run inspect_test_list_pinmode fail")
                return False, list_fail_arry
        else:
            logger.error(f"args error target_mode is {target_mode}")

        logger.info("run test_flow_for_linux pass")
        return True, list_fail_arry

    @sysapp_print.print_line_info
    def printf_list_whitelist(self):
        """printf information for whitelist

        Args:
            Na

        Returns:
            Na
        """
        for item in self.list_whitelist_pin_mode:
            logger.warning("----------------------------------------")
            logger.warning(f"pin index           is {item['pin_index']}")
            logger.warning(f"pin name            is {item['pin_name']}")
            logger.warning(f"pin pin_mode_name   is {item['pin_mode_name']}")
            logger.warning(f"pin pin_used_reason is {item['pin_used_reason']}")
            logger.warning("----------------------------------------")
