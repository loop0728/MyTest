"""Base Bsp Function Class"""
#!/usr/bin/python3
# -*- coding: utf-8 -*-

# from cases.platform.bsp.sysapp_bsp_base_val import DEFAULT_MODULE_PATH

class SysappBspBase:
    """ Base class for bsp case """

    def __init__(self, msg_handle=None):
        """ Init func.

        Args:
            MsgHandle: client handle used to transfer command
        """

        if msg_handle is None:
            raise Exception("msg_handle has't be set")
        self.msg_handle = msg_handle

        try:
            DEFAULT_MODULE_PATH
        except NameError:
            self.module_path = "/lib/modules/5.10.117/"
        else:
            self.module_path = DEFAULT_MODULE_PATH

    def insmod(self):
        """ Insmod func. """

        pass

    def rmmod(self):
        """ Insmod func. """

        pass

    def read(self, args, timeout=0):
        """
        Bsp base read func.

        Args:
            args      : argument to be filled
            timeout   : max timeout argument
        """
        pass

    def write(self, args, timeout=0):
        """
        Bsp base write func.

        Args:
            args      : argument to be filled
            timeout   : max timeout argument
        """
        pass

    def run(self, args, background=False):
        """
        Bsp base run feature function.

        Args:
            args      : argument to be filled
            timeout   : max timeout argument
            background: run demo at background or not
        """
        pass

    def exit(self, args, timeout=0):
        """
        Bsp Done function, which pair with run function
        when demo exec pending or run at background.

        Args:
            args      : argument to be filled
        """
        pass

    def check_result(self, args):
        """
        Bsp Done function, which pair with run function
        when demo exec pending or run at background.

        Args:
            args      : argument to be filled
        """
        pass

    def __del__(self):
        """ deinit func """
        pass
