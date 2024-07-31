#!usr/bin/python
# -*- coding: utf-8 -*-

#__all__ = ['_rs232_contrl']

import serial
import time
import platform

class rs232_contrl():

    def __init__(self, relay, com='/dev/relay_uart', baudrate=9600):
        os_info = platform.system()
        port_info = com
        if os_info == 'Windows':
            port_info = 'COM' + com
        self.relay = relay
        self.power_off_arr = [0x33, 0x01, 0x11, 0x00, 0x00, 0x00, 0x00, 0x45]
        self.power_on_arr = [0x33, 0x01, 0x12, 0x00, 0x00, 0x00, 0x00, 0x46]
        self.power_off_arr[6] = self.power_off_arr[6] + relay
        self.power_off_arr[7] = self.power_off_arr[7] + relay
        self.power_on_arr[7] = self.power_on_arr[7] + relay
        self.power_on_arr[6] = self.power_on_arr[6] + relay
        try_time = 0
        while True:
            try:
                self.rs232ser = serial.Serial(baudrate=9600, port=port_info, timeout=0.05)
                break
            except Exception as e:
                print(e)
                time.sleep(1)
                try_time += 1
                if try_time > 100:
                    raise
        self.isOpen = self.rs232ser.isOpen

    def power_off(self):
        if self.isOpen:
            print("[%s] power off relay:%s" % (
            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())), self.relay))
            self.rs232ser.write(self.power_off_arr)
        else:
            print("power_off open failed")

    def power_on(self):
        if self.isOpen:
            print("[%s] power on relay:%s" % (
            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())), self.relay))
            self.rs232ser.write(self.power_on_arr)
        else:
            print("power_on open failed")

    def isOpen(self) -> bool:
        return self.isOpen

    def close(self):
        self.isOpen = False
        self.rs232ser.close()
        print("close rs232ser")
