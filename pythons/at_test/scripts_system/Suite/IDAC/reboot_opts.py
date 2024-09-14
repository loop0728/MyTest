import time
from PythonScripts.logger import logger

class RebootOpts():
    def __init__(self, device):
        self.device = device
        self.borad_cur_state = ''

    def get_cur_boot_state(self):
        result = 255
        print(f"get_cur_boot_state !!!!!!!!!!!!!!!!!!!!")
        self.device.write('\n')
        self.borad_cur_state = self.device.get_borad_cur_state()[1]
        if self.borad_cur_state != 'Unknow':
            result = 0
        else:
            for i in range(1,20):
                self.device.write('')
                self.borad_cur_state = self.device.get_borad_cur_state()[1]
                if self.borad_cur_state != 'Unknow':
                    result = 0
                    break
                time.sleep(1)

        if self.borad_cur_state == 'Unknow':
            logger.print_error("dev is not at kernel or at uboot")
        return result

    def kernel_to_uboot(self):
        result = 255
        try_time = 0
        logger.print_info('begin to run kernel_to_uboot')
        result = self.get_cur_boot_state()
        if result != 0:
            return result
        logger.print_info(f'cur_state: {self.borad_cur_state}')
        if self.borad_cur_state != 'at kernel':
            logger.print_error(f"dev is not at kernel now, cur_state:{self.borad_cur_state}")
            result = 255
            return result

        self.device.write('reboot -f')
        time.sleep(2)
        self.device.clear_borad_cur_state()

        logger.print_info("begin to read keyword")
        # wait uboot keyword
        while True:
            status,line = self.device.read(1, 10)
            if status == True:
                if isinstance(line, bytes):
                    line = line.decode('utf-8', errors='replace').strip()
                if "Auto-Negotiation" in line:
                    break
            else:
                logger.print_error("read line fail")
                result = 255
                return result

        # enter to uboot
        while True:
            if try_time >= 30:
                logger.print_error("enter to uboot timeout")
                result = 255
                break
            self.device.write('')
            self.borad_cur_state = self.device.get_borad_cur_state()[1]
            if self.borad_cur_state == 'at uboot':
                logger.print_info("enter to uboot success")
                result = 0
                break
            elif self.borad_cur_state == 'at kernel':
                logger.print_error("enter to uboot fail")
                result = 255
                break
            try_time += 1
            time.sleep(0.1)
        return result

    def uboot_to_kernel(self):
        result = 255
        try_time = 0
        result = self.get_cur_boot_state()
        if result != 0:
            return result
        if self.borad_cur_state != 'at uboot':
            logger.print_error("dev is not at uboot now")
            result = 255
            return result

        self.device.write('reset')
        self.device.clear_borad_cur_state()

        while True:
            if try_time >= 30:
                logger.print_error("enter to kernel timeout")
                result = 255
                break
            self.borad_cur_state = self.device.get_borad_cur_state()[1]
            if self.borad_cur_state == 'at kernel':
                logger.print_info("enter to kernel success")
                result = 0
                break
            try_time += 1
            time.sleep(1)
        return result

    def kernel_to_kernel(self):
        result = 255
        try_time = 0
        result = self.get_cur_boot_state()
        if result != 0:
            return result
        if self.borad_cur_state != 'at kernel':
            logger.print_error("dev is not at kernel now")
            result = 255
            return result

        self.device.write('reboot -f')
        time.sleep(2)
        self.device.clear_borad_cur_state()

        while True:
            if try_time >= 30:
                logger.print_error("enter to kernel timeout")
                result = 255
                break
            self.borad_cur_state = self.device.get_borad_cur_state()[1]
            if self.borad_cur_state == 'at kernel':
                logger.print_info("enter to kernel success")
                result = 0
                break
            try_time += 1
            time.sleep(1)
        return result

    def uboot_to_uboot(self):
        result = 255
        try_time = 0
        result = self.get_cur_boot_state()
        if result != 0:
            return result
        if self.borad_cur_state != 'at uboot':
            logger.print_error("dev is not at uboot now")
            result = 255
            return result

        self.device.write('reset')
        self.device.clear_borad_cur_state()

        # wait uboot keyword
        while True:
            status,line = self.device.read()
            if status == True:
                if isinstance(line, bytes):
                    line = line.decode('utf-8', errors='replace').strip()
                if "Auto-Negotiation" in line:
                    break
            else:
                logger.print_error("read line fail")
                result = 255
                return result

        # enter to uboot
        while True:
            if try_time >= 30:
                logger.print_error("enter to uboot timeout")
                result = 255
                break
            self.device.write('')
            self.borad_cur_state = self.device.get_borad_cur_state()[1]
            if self.borad_cur_state == 'at uboot':
                logger.print_info("enter to uboot success")
                result = 0
                break
            elif self.borad_cur_state == 'at kernel':
                logger.print_error("enter to uboot fail")
                result = 255
                break
            try_time += 1
            time.sleep(0.1)
        return result
