#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""security boot case base"""

import textwrap
import re
import time
import sys
import threading
from typing import List, Dict, Union, Optional, Tuple
from colorama import Fore, Style
import click

from suite.common.sysapp_common_utils import write_and_match_keyword
from suite.common.sysapp_common_utils import _match_keyword as match_keyword
from suite.common.sysapp_common_logger import logger
from suite.common.sysapp_common_device_opts import SysappDeviceOpts
from suite.bsp.common.sysapp_bsp_storage import SysappBspStorage
from cases.platform.bsp.complex_cases.security_boot.sysapp_bsp_security_boot_base_var import (
    SECURITY_BOOT_PARTITION_EXPECTED_LOG,
)


class SysappBspSecurityBootBase:
    """Security boot base

    Test Info
    Swcurity boot test case base class

    Attributes:
            case_uart (handle): case uart handle
    """

    def __init__(self, case_uart):
        """Case Init function

        Args:
            case_uart: uart conlse
        """
        # super().__init__(case_name="s", case_run_cnt=1, script_path='/')
        self.uart = case_uart
        self.storage = SysappBspStorage(self.uart)
        self.security_boot_partition_expected_log = SECURITY_BOOT_PARTITION_EXPECTED_LOG
        logger.info("SysappBspSecurityBootBase init successful")

    @staticmethod
    def interactive_reminder(
        prompt_text: str,
        interaction_type: str = "confirm",
        choices: Optional[List[Dict[str, Union[int, str]]]] = None,
        default: Optional[Union[bool, str, int]] = None,
    ) -> Union[bool, str, Dict[str, Union[int, str]]]:
        """interactive reminder
        Args:
            prompt_text (str): Display prompt text to users
            interaction_type (str,optional): Interaction type. The optional values are
            'confirm', 'prompt', or 'choice'. The default is 'confirm'.
            choices (list,optional): When the interaction_type is 'choice', it is a list of
            dictionaries with keys 'number', 'name', and 'description'. The default is None.
            default (Union[bool, str, int],optional): Default value. The default is None.
        Raises:
            ValueError: If an unsupported interaction_type is provided.
        Returns:
            Union[bool, str, Dict[str, Union[int, str]]]:
            - 'confirm': bool
            - 'prompt': str
            - 'choice': dict with keys 'number', 'name', and 'description'
        """
        formatted_prompt = textwrap.dedent(prompt_text).strip()
        print("")
        click.echo(formatted_prompt)

        if interaction_type == "confirm":
            return click.confirm(
                "确认？", default=default if isinstance(default, bool) else True
            )
        elif interaction_type == "prompt":
            return str(
                click.prompt(
                    "请输入",
                    default=default if isinstance(default, str) else "",
                    type=str,
                )
            )
        elif interaction_type == "choice":
            if not choices or not all(
                "number" in choice and "name" in choice and "description" in choice
                for choice in choices
            ):
                raise ValueError(
                    "Choices must be provided as a list of dictionaries"
                    "with keys 'number', 'name', and 'description'"
                )
            for choice in choices:
                click.echo(f"{choice['number']}: {choice['description']}")
            valid_choices = [choice["number"] for choice in choices]
            while True:
                selection = click.prompt(
                    "请输入选项编号",
                    type=int,
                    default=default if isinstance(default, int) else None,
                )
                if selection in valid_choices:
                    return next(
                        choice for choice in choices if choice["number"] == selection
                    )
                else:
                    click.echo("无效的选择。请输入有效的选项编号。")
        else:
            raise ValueError(f"Unsupported interaction type: {interaction_type}")

    def get_images_filename_frome_sd(self) -> Tuple[bool, List[str]]:
        """Get images filename from SD card with validation and sorting.

        Match image filenames using the following pattern:
        1. Starts with "SigmastarUpgradeSD_"
        2. Followed by partition name that must exist in security_boot_partition_expected_log
        3. Ends with ".bin"

        The returned image list will be sorted according to the order in
        security_boot_partition_expected_log.

        Returns:
            Tuple:
            - bool: True for succeed, False for failed
            - list: Sorted valid images file names
        """
        # Check board state and get partition data
        if self.uart.check_uboot_phase():
            cmd = "fatls mmc 0:1"
            ret, data = write_and_match_keyword(self.uart, cmd, "SigmaStar #", True)
            if ret is False:
                logger.error(f"Failed to execute command: {cmd}")
                return False, []
        else:
            logger.error("Failed to verify board state. Please check board status.")
            return False, []

        # Find and validate all matching image files
        image_pattern = r"SigmastarUpgradeSD_(.*?)\.bin"
        matches = re.finditer(image_pattern, data)
        valid_images = []
        partition_keys = list(self.security_boot_partition_expected_log.keys())

        for match in matches:
            full_name = match.group(0)  # Complete filename
            partition_name = match.group(1)  # Extracted partition name

            # Validate partition name
            if partition_name not in partition_keys:
                logger.error(
                    f"{full_name} 不在预期的测试列表中，请找开发人员确认此镜像文件再继续测试"
                )
                return False, []
            valid_images.append((full_name, partition_keys.index(partition_name)))

        if not valid_images:
            logger.error("No valid image files found")
            return False, []

        # Sort images based on security_boot_partition_expected_log order and extract filenames
        sorted_images = [image[0] for image in sorted(valid_images, key=lambda x: x[1])]

        return True, sorted_images

    def ensure_entry_uboot_while_power_on(
        self,
        timeout_seconds: float = 50.0,
        except_log: Optional[List[str]] = None,
        boot_interrupt_attempts: int = 20,
    ) -> bool:
        """
        Monitor UART output and send periodic Enter keys to enter uboot using three threads.
        Display real-time countdown and return True when successfully entered uboot.

        Args:
            timeout_seconds: Maximum time to wait for uboot entry (seconds)
            except_log: Except log
            boot_interrupt_attempts: boot interrupt attempts

        Returns:
            bool: True if successfully entered uboot, False if timeout

        Raises:
            TimeoutError: If failed to enter uboot within timeout period
        """
        if except_log is None:
            except_log = ["Hit any key to stop autoboot", "SigmaStar #"]
        uboot_prompt = "SigmaStar #"

        found_event = threading.Event()
        stop_event = threading.Event()

        def display_timer():
            """Thread function for displaying countdown"""
            start_time = time.monotonic()
            while not stop_event.is_set():
                current_time = time.monotonic()
                remaining_time = timeout_seconds - (current_time - start_time)
                if remaining_time <= 0:
                    break
                sys.stdout.write(f"\r请在 {remaining_time:.1f} s 内完成对板子的上电")
                sys.stdout.flush()
                time.sleep(0.1)
            sys.stdout.write("\n\n")
            sys.stdout.flush()

        def send_enter():
            """Thread function for sending enter keys and match uboot prompt"""
            send_str = "\n" * boot_interrupt_attempts
            while True:
                _, data = self.uart.read(wait_timeout=int(timeout_seconds))
                if any(log in data for log in except_log):
                    self.uart.write(data=send_str)
                    break
            ret, data = match_keyword(
                self.uart,
                keyword=uboot_prompt,
                max_read_lines=1500,
                timeout=int(timeout_seconds),
            )

            if ret is True:
                found_event.set()

        # Create and start threads
        timer_thread = threading.Thread(target=display_timer)
        enter_thread = threading.Thread(target=send_enter)
        timer_thread.start()
        enter_thread.start()

        # Wait until uboot prompt is found or timeout
        found = found_event.wait(timeout=timeout_seconds)
        if not found:
            logger.error(f"Failed to enter uboot within {timeout_seconds} seconds")

        # Stop all threads
        stop_event.set()

        # Wait for threads to end
        timer_thread.join(timeout=1.0)
        enter_thread.join(timeout=1.0)

        # Check if threads exited normally
        if timer_thread.is_alive():
            logger.warning("Timer thread did not end within 1 second")
        if enter_thread.is_alive():
            logger.warning("Enter key thread did not end within 1 second")

        return found

    def burn_image_from_sd(
        self, image_name: str, bootdelay: int = 5, timeout_seconds: int = 50
    ) -> bool:
        """burning images by file in the sd

        Args:
            image_name: the image file name

        Returns:
            bool: True for succeed, False for failed
        """
        # set bootdelay
        cmd = f"set bootdelay {bootdelay}"
        ret, _ = write_and_match_keyword(
            self.uart,
            cmd,
            "SigmaStar #",
        )
        if ret is False:
            logger.error(f"{cmd} execute fail")
            return ret

        # saveenv
        cmd = "saveenv"
        ret, _ = write_and_match_keyword(
            self.uart,
            cmd,
            "SigmaStar #",
        )
        if ret is False:
            logger.error(f"{cmd} execute fail")
            return ret

        # burning image
        cmd = f"sdstar -i 0:1 -f {image_name}"
        ret, _ = write_and_match_keyword(
            self.uart, cmd, ">> reset", max_read_lines=1500, timeout=timeout_seconds
        )
        if ret is False:
            logger.error(f"{cmd} execute fail")
            return ret

        return ret

    def verify_boot_log(
        self,
        partition: str,
        timeout_seconds: float = 50.0,
        boot_interrupt_attempts: int = 30,
    ) -> bool:
        """verify boot log

        Args:
            partition(str): partition name
            timeout_seconds(float): timeout(seconds)

        Returns:
            bool: True for succeed, False for failed
        """
        if partition not in self.security_boot_partition_expected_log.keys():
            logger.error(
                f"Partition '{partition}' not found in expected errors dictionary"
            )
            return False

        expected_error = self.security_boot_partition_expected_log.get(partition, "")
        if not expected_error:
            logger.error(f"No expected error defined for partition '{partition}'")
            return False
        else:
            print(f"{partition} security boot 测试期望的打印：{expected_error}")

        found_event = threading.Event()

        def display_timer():
            """Thread function for displaying countdown"""
            start_time = time.monotonic()
            while not found_event.is_set():
                current_time = time.monotonic()
                remaining_time = timeout_seconds - (current_time - start_time)
                if remaining_time <= 0:
                    break
                sys.stdout.write(f"\r检测启动log中，剩余：{remaining_time:.1f} s")
                sys.stdout.flush()
                time.sleep(0.1)
            sys.stdout.write("\n")
            sys.stdout.flush()

        def read_uart():
            """Thread function for match expecte log"""
            send_str = "\n" * boot_interrupt_attempts
            if partition == "uboot":
                while True:
                    _, data = self.uart.read(wait_timeout=int(timeout_seconds))
                    if "E:CD" in data:
                        self.uart.write(
                            data=send_str,
                        )
                        break

            ret, data = match_keyword(
                self.uart,
                keyword=expected_error,
                max_read_lines=1500,
                timeout=int(timeout_seconds),
            )
            if ret is True:
                found_event.set()
                timer_thread.join(timeout=1.0)
                if timer_thread.is_alive():
                    logger.error("Warning: Timer thread did not end within 1 second")
                print(
                    f"检测到 {partition} security boot 期望的打印：{data.strip()}",
                    flush=True,
                )
            else:
                print(f"没有检测到 {partition} security boot 期望的打印", flush=True)

        timer_thread = threading.Thread(target=display_timer)
        uart_thread = threading.Thread(target=read_uart)
        timer_thread.start()
        uart_thread.start()

        found = found_event.wait(timeout=timeout_seconds)
        if not found:
            logger.error(f"Failed to verify uboot log within {timeout_seconds} seconds")

        uart_thread.join(timeout=1.0)
        if uart_thread.is_alive():
            logger.error("Warning: UART monitor thread did not end within 1 second")

        return found

    def test_partition(self, image_name: str) -> bool:
        """test security_boot's burning and verify boot log

        Args:
            image_name(str): images file name

        Returns:
            bool: True for succeed, False for failed
        """
        ret = False
        prefix = "SigmastarUpgradeSD_"
        suffix = ".bin"

        if image_name.startswith(prefix) and image_name.endswith(suffix):
            partition = image_name[len(prefix) : -len(suffix)]
        else:
            logger.error(f"Invalid image name format: {image_name}")
            return False

        print(
            f"\n{Fore.BLUE}==> 准备测试 {partition} 的 security boot:{Style.RESET_ALL}"
        )
        ret = self.burn_image_from_sd(image_name)
        if ret is False:
            logger.error("burn_image_from_sd failed")
            return ret
        else:
            print(
                f"烧录 {image_name} 完成，请先将板子下电 -> 拔出 SD 卡 -> 重新上电，准备验证启动 log"
            )

        return self.verify_boot_log(partition)

    def erase_flash_to_empty(self) -> bool:
        """erase flash to empty

        Returns:
            ret: bool
        """
        ret = False

        ret, partition_list = SysappDeviceOpts.get_partition_list(self.uart)
        if ret:
            logger.debug(f"get partitons: {partition_list}")
        else:
            logger.error("get partitons fail")
            return ret

        if self.uart.check_uboot_phase():
            for partiton in partition_list:
                mtd_name = partiton[1]
                print(mtd_name)
                ret = self.storage.erase(mtd_name, None)
                if ret is False:
                    logger.error(f"erase {mtd_name} fail")
                    return ret
        elif self.uart.check_kernel_phase():
            for partiton in partition_list:
                mtd_num = partiton[0]
                mtd_name = partiton[1]
                print(mtd_name)
                ret = self.storage.erase(f"/dev/mtd{mtd_num}", None)
                if ret is False:
                    logger.error(f"erase {mtd_name} fail")
                    return ret
        else:
            logger.error("please check board state")
            ret = False

        return ret
