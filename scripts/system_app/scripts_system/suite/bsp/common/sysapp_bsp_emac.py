""" Emac Function Class"""
#!/usr/bin/python3
# -*- coding: utf-8 -*-

from suite.bsp.common.sysapp_bsp_base import SysappBspBase

class SysappBspEmac(SysappBspBase):
    """ Emac class for bsp case """

    def insmod(self):
        """ Insmod func. """

        #cmd = self.module_path + "/" + "sstar_gmac.ko";
        pass

    def rmmod(self):
        """ Rmmod func. """

        #cmd = "sstar_gmac";
        pass
