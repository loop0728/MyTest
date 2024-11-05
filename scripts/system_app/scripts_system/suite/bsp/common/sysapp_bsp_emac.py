""" Emac Function Class"""
#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sysapp_platform as platform
from suite.bsp.common.sysapp_bsp_base import SysappBspBase
import suite.common.sysapp_common_utils as sys_common
from suite.common.sysapp_common_logger import logger
from sysapp_client import SysappClient

class SysappBspEmac(SysappBspBase):
    """ Emac class for bsp case """

    def __init__(self, uart_name):
        """
        init func

        Args:
            uart_name: uart name
        """
        if not isinstance(uart_name,SysappClient):
            raise TypeError(f"{uart_name} parameters must be SysappClient ")

        if uart_name.is_open is True:
            self.uart = uart_name
        else:
            raise ValueError("uart_name.is_open must be True ")
        super().__init__(self.uart)

    def insmod(self):
        """ Insmod func. """
        ret=sys_common.insmod_ko(self.uart,f"{self.module_path}/sstar_emac.ko","")
        if ret is False:
            logger.error("insmod_ko failed")
        return ret

    def rmmod(self):
        """ Rmmod func. """
        ret=sys_common.rmmod_ko(self.uart,f"{self.module_path}/sstar_emac.ko")
        if ret is False:
            logger.error("rmmod_ko failed")
        return ret


    def run(self, args, background=False):
        """
        Bsp base run feature function.

        Args:
            args      : argument to be filled
            timeout   : max timeout argument
            background: run demo at background or not
        """
        run_in_back=" "
        time_para=" -c 5 "
        if background:
            run_in_back="&"
        if args=="forever":
            time_para=" -w 1000 "
        cmd = f"ping -W 5 {time_para} {platform.PLATFORM_MOUNT_IP} {run_in_back}"
        ret, _ =sys_common.write_and_match_keyword(self.uart,cmd," ",False,20,20)
        if ret is False:
            logger.error(f"{cmd} failed")
        return ret


    def exit(self, args, timeout=0):
        """
        Bsp Done function, which pair with run function
        when demo exec pending or run at background.

        Args:
            args      : argument to be filled
        """
        cmd = "pkill -9 ping"
        ret, _ =sys_common.write_and_match_keyword(self.uart,cmd,"ping -W 5",False,2000,20)
        if ret is False:
            logger.error(f"{cmd} failed")
        return ret

    def check_result(self, args):
        """
        Bsp Done function, which pair with run function
        when demo exec pending or run at background.

        Args:
            args      : argument to be filled
        """
        cmd = "\n"
        ret, _ =sys_common.write_and_match_keyword(self.uart,cmd,"64 bytes from",False,2000,20)
        if ret is False:
            logger.error(f"{cmd} failed")
        return ret
