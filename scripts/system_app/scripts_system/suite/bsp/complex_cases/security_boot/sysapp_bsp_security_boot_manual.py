#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""test for security boot with manual"""

from typing import List, Optional
from colorama import Fore, Style

from suite.common.sysapp_common_utils import _match_keyword as match_keyword
from suite.common.sysapp_common_logger import logger, sysapp_print
from suite.common.sysapp_common_reboot_opts import SysappRebootOpts
from suite.common.sysapp_common_case_base import SysappCaseBase as CaseBase
from suite.common.sysapp_common_types import SysappErrorCodes as EC
from suite.bsp.complex_cases.security_boot.sysapp_bsp_security_boot_base import (
    SysappBspSecurityBootBase,
)
from sysapp_client import SysappClient


class SysappBspSecurityBootManual(CaseBase):
    """Sysapp BSP security boot manual class

    Attributes:
        manual_prompt: for manual prompt
        case_name: case name
        case_run_cnt: case run cnt
        script_path: script path
        uart: uart
        security_base: security base
    """

    class SysappSecurityBootManualPrompt:
        """
        Prompt message class for storing and managing various prompt messages during
        Security Boot testing.Including environment confirmation, upgrade preparation,
        power-on and test mode selection prompts.
        """

        def __init__(self):
            self.prepare_confirm_empty_flash = f"""
            当前板子是否还没有擦除至空片状态？
            y: 若板子不是空片，则会先将板子擦除至空片状态
               {Fore.YELLOW}注意：
               1、初始环境下，板子均不是空片状态，测试人员默认选择 y 即可
               2、若选择此项，则需保证 SD 卡拔出 -> 再将板子上电{Style.RESET_ALL}
            N: 若当前环境已擦除至空片，则会跳过擦除分区，直接进入 security boot 测试流程
            """

            self.prepare_upgrade_by_sd = f"""
            请确保以下事项已经准备好：
            {Fore.YELLOW}1、将板子下电（先不要上电）
            2、将 image_secure/Sd_Upgrade/ 文件夹内的文件拷贝到SD卡（确保SD卡为FAT32格式）中
            3、将SD卡插入板子卡槽
            4、保证拨码开关为对应flash的启动项（注意不是那个带有skip sd的）{Style.RESET_ALL}
            """

            self.sequential_test = f"""
            顺序执行。将按照启动流程测试 security boot image{Fore.YELLOW}（默认情况下，测试人员请选择此项）{Style.RESET_ALL}
            """

            self.selective_test = """选择执行。将选择要测试哪一个security boot image"""

        def get_all_prompts(self):
            """
            Get all prompt messages.

            Returns:
                dict: Dictionary containing all prompt messages
            """
            return {
                "empty_flash": self.prepare_confirm_empty_flash,
                "upgrade_sd": self.prepare_upgrade_by_sd,
                "sequential": self.sequential_test,
                "selective": self.selective_test,
            }

    manual_prompt = SysappSecurityBootManualPrompt()

    def __init__(self, case_name, case_run_cnt=1, script_path="./"):
        """case init function

        Args:
            case_name (str): case name
            case_run_cnt (int): case run cnt
            script_path (str): script path
        """
        super().__init__(case_name, case_run_cnt, script_path)
        self.case_name = case_name
        self.case_run_cnt = case_run_cnt
        self.script_path = script_path
        self.uart = SysappClient(self.case_name, "uart", "uart")
        self.security_base = SysappBspSecurityBootBase(self.uart)

        logger.info(f"{self.case_name} init successful")

    @sysapp_print.print_line_info
    def case_deinit(self):
        """case deinit function

        Returns:
            bool: True
        """
        result = SysappRebootOpts.reboot_to_kernel(self.uart)
        if result is False:
            logger.error("case_deinit Fail")

        logger.info("run case_deinit succeed")
        return True

    def sequential_test(self, available_images: List[str]) -> bool:
        """Test images sequentially in the order they are provided.

        Args:
            available_images: List of sorted and validated image files

        Returns:
            bool: True for succeed, False for failed
        """
        results = {}
        total_images = len(available_images)

        for index, image in enumerate(available_images):
            # Test current partition
            result = self.security_base.test_partition(image)
            results[image] = result
            if result is True:
                print(f"{Fore.GREEN}{image} 测试结果：通过{Style.RESET_ALL}")
            else:
                print(
                    f"{Fore.RED}{image} 测试结果：失败。终止后续测试{Style.RESET_ALL}"
                )
                return False

            # If not the last image, prompt for next test
            if index < total_images - 1:
                next_image = available_images[index + 1]
                print(
                    f"\n请先将板子下电 -> 插入sd卡，以继续下一个镜像文件的测试：{next_image}"
                )
                ret = self.security_base.ensure_entry_uboot_while_power_on()
                if ret is False:
                    logger.error("ensure_entry_uboot_while_power_cycle failed")
                    return False

        return True

    def selective_test(self, available_images: List[str]) -> bool:
        """
        Let users select specific image file to test.

        Args:
            available_images: List of available image files
        Returns:
            bool: True if test succeeds, False if test fails or user quits
        """
        while True:
            # Display list of available images
            print("\n可测试的镜像文件：")
            for idx, image in enumerate(available_images):
                print(f"{idx}. {image}")

            # Get user input using interactive_reminder
            result = self.security_base.interactive_reminder(
                "请选择要测试的镜像编号（输入'q'退出测试）：",
                interaction_type="prompt",
                default="0",
            )
            choice = str(result)

            # Check if user wants to quit
            if choice.lower() == "q":
                print("\n用户选择退出测试")
                return True

            # Validate input and perform test
            try:
                idx = int(choice)
                if 0 <= idx < len(available_images):
                    selected_image = available_images[idx]

                    # Test the selected image
                    result = self.security_base.test_partition(selected_image)
                    if result is True:
                        print(
                            f"{Fore.GREEN}{selected_image} 测试结果：通过{Style.RESET_ALL}"
                        )
                    else:
                        print(
                            f"{Fore.RED}{selected_image} 测试结果：失败。终止后续测试{Style.RESET_ALL}"
                        )
                        return False

                    # Ask if user wants to continue testing
                    next_test = self.security_base.interactive_reminder(
                        "\n是否继续测试其他镜像？",
                        interaction_type="confirm",
                        default=True,
                    )

                    if not next_test:
                        print("\n用户选择退出测试")
                        return True

                    print("请将板子下电 -> 插入sd卡，以继续测试")
                    self.security_base.ensure_entry_uboot_while_power_on()
                else:
                    print(
                        f"输入序号无效，请输入 0-{len(available_images)-1} 之间的数字，或输入 q 退出"
                    )
                    continue

            except ValueError:
                print("输入格式错误，请输入数字或字符'q'")
                continue

    def prepare_empty_flash(self) -> bool:
        """prepare empty flash env

        Returns:
            bool: True for succeed, False for failed
        """
        ret = False

        ret = self.security_base.interactive_reminder(
            self.manual_prompt.prepare_confirm_empty_flash,
            interaction_type="confirm",
            default=True,
        )
        if isinstance(ret, bool):
            if ret is True:
                self.uart.write(data="ls", echo_check=False)
                ret = match_keyword(
                    self.uart, keyword="/ #", max_read_lines=1500, timeout=50
                )
                if ret is False:
                    logger.error("entry kernel fail")
                    return ret

                ret = self.security_base.erase_flash_to_empty()
                if ret is False:
                    logger.error("erase_flash_to_empty failed")
                else:
                    print("已成功将板子擦除至空片")
            return True
        else:
            logger.error("interactive_reminder get failed")
            return False

    def check_test_environment(self) -> bool:
        """check test enc

        Returns:
            bool: True for succeed, False for failed
        """
        ret = self.security_base.interactive_reminder(
            self.manual_prompt.prepare_upgrade_by_sd,
            interaction_type="confirm",
            default=False,
        )
        if ret is False:
            logger.warning(
                "Exit because the environment for manual testing is not prepared yet."
            )
            return False
        else:
            return True

    def boot_and_get_images_list(self) -> Optional[list]:
        """boot and get iamges list

        Returns:
            - list: Sorted valid images file names
        """
        ret = self.security_base.ensure_entry_uboot_while_power_on()
        if ret is False:
            logger.error("entry uboot fail")
            return None

        ret, available_images = self.security_base.get_images_filename_frome_sd()
        if ret is False:
            logger.error("get images file name fail")
            return None
        else:
            return available_images

    def execute_selected_method_test(self, available_images: List[str]) -> bool:
        """execute selected method test

        Args:
            available_images: available images list

        Returns:
            bool: True for succeed, False for failed
        """
        result = self.security_base.interactive_reminder(
            "请选择测试方式：",
            interaction_type="choice",
            choices=[
                {
                    "number": 0,
                    "name": "sequential_test",
                    "description": self.manual_prompt.sequential_test.strip(),
                },
                {
                    "number": 1,
                    "name": "selective_test",
                    "description": self.manual_prompt.selective_test.strip(),
                },
            ],
            default=0,
        )

        if isinstance(result, dict) and result.get("name"):
            if result["name"] == "sequential_test":
                ret = self.sequential_test(available_images)
            else:
                ret = self.selective_test(available_images)

            return ret
        else:
            logger.error("get test method failed")
            return False

    @sysapp_print.print_line_info
    def runcase(self):
        """Run case entry.

        Args:
            Na

        Returns:
            enum: ErrorCodes code
        """
        err_code = EC.SUCCESS

        # 1. ensure that the board is empty
        ret = self.prepare_empty_flash()
        if ret is False:
            err_code = EC.FAIL
            return err_code

        # 2. ensure that required for test is ready
        ret = self.check_test_environment()
        if ret is False:
            err_code = EC.FAIL
            return err_code

        # 3. boot to uboot from SD & get images file list
        available_images = self.boot_and_get_images_list()
        if not available_images:
            err_code = EC.FAIL
            return err_code

        # 4. choose the testing method & execute: sequential execution or selective execution
        ret = self.execute_selected_method_test(available_images)
        if ret is False:
            err_code = EC.FAIL
            return err_code

        return err_code
