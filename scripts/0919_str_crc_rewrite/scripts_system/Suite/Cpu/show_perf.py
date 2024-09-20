import time
import threading
from PythonScripts.logger import logger
from Common.case_base import CaseBase
from client import Client
import Common.system_common as sys_common
import PythonScripts.variables as platform

class MixerThread(threading.Thread):
    def __init__(self, telnet_handle):
        threading.Thread.__init__(self)
        self.telnet_handle = telnet_handle

    def run(self):
        cmd = "cd /mnt/scripts/pipeline_iford; ./amicmd --json ./json_out/1snr_4m20p_ipu_vdf/menu_in.json ./json_out/1snr_4m20p_ipu_vdf/isp_3dnr/isp0_3dnr_0.json -l 0x100"
        self.telnet_handle.write(cmd)
        for i in range(1, 25):
            logger.print_warning(f"cnt={i}")
            time.sleep(1)
        cmd = "y"
        self.telnet_handle.write(cmd)
        time.sleep(5)
        self.telnet_handle.close()

class show_perf(CaseBase):
    def __init__(self, case_name, case_run_cnt=1, module_path_name='./'):
        super().__init__(case_name, case_run_cnt, module_path_name)
        self.uart = Client(self.case_name, "uart", "uart")
        self.subpath = "iford_systemapp_interrupt_testcase"

    def get_ko_insmod_state(self, koname):
        result = ""
        cmd = f"lsmod | grep {koname} | wc -l"
        # 检查串口信息
        res = self.uart.write(cmd)
        if res is False:
            logger.print_error(f"{self.uart} is disconnected.")
            return "Unknown"
        wait_keyword = "0"
        status, data = self.uart.read()
        if status  == True:
            if wait_keyword in data:
                result = "none"
                return result
            else:
                result = "insmod"
                return result
        else:
            result = "Unknown"
            return result

    def get_current_os(self):
        wait_keyword = "none"
        data = self.get_ko_insmod_state("mi_sys")
        if wait_keyword in data:
            result = "dualos"
            return result
        else:
            result = "purelinux"
            return result

    def check_insmod_ko(self, koname):
        wait_keyword = "none"
        ko_path = f"/config/modules/5.10/{koname}.ko"
        data = self.get_ko_insmod_state(f"{koname}")
        if wait_keyword in data:
            cmd = f"insmod {ko_path}"
            logger.print_warning(f"we will {cmd}")
            self.uart.write(cmd)
            result = "true"
            return result
        else:
            logger.print_warning(f"we no need insmod {koname}")
            result = "false"
            return result

    def switch_os(self, target_os):
        result = 0
        cur_os = self.get_current_os()
        if cur_os == target_os:
            logger.print_warning(f"[{self.case_name}] current os is match {target_os}")
            return 0

        logger.print_warning(f"will switch to OS({target_os})!")
        if target_os == "dualos":
            cmd = "cd /customer/sample_code/bin/"
            self.uart.write(cmd)
            wait_keyword = "/customer/sample_code/bin #"
            status, data = self.uart.read()
            if status  == True:
                if wait_keyword not in data:
                    return 255
            else:
                logger.print_error(f"Read fail,no keyword: {wait_keyword}")
                return 255
            cmd = "./prog_aov_aov_demo -t"
            self.uart.write(cmd)
            time.sleep(10)
            cmd = "c"
            self.uart.write(cmd)

        if target_os == "purelinux":
            cmd = "cd /customer/sample_code/bin/"
            self.uart.write(cmd)
            time.sleep(1)
            wait_keyword = "/customer/sample_code/bin #"
            status, data = self.uart.read()
            if status == True:
                if wait_keyword not in data:
                    result = 255
                    return result

            cmd = "./prog_preload_linux -t"
            wait_keyword = "press c to change mode"
            result, data = sys_common.write_and_match_keyword(self.uart, cmd, wait_keyword)
            if result == False:
                return 255

            cmd = "c"
            self.uart.write(cmd)

        time.sleep(20)
        return result

    def runcase(self):
        result = 0
        mount_path = f"{platform.mount_path}/{self.subpath}"
        # step1 判断是否在kernel下
        result = sys_common.goto_kernel(self.uart)
        if result != True:
            logger.print_warning(f"caseName[{self.case_name}] not in kernel!")
            return 255
        # step2 切换到dualos
        if self.case_name == "show_cpu_dualos":
            result = self.switch_os("dualos")
            if result == 255:
                logger.print_warning(f"caseName[{self.case_name}] run done!")
                return 255
        # step3 挂载网络
        logger.print_warning("config network")
        self.check_insmod_ko("sstar_emac")
        sys_common.set_board_kernel_ip(self.uart)
        # step4 mount nfs
        logger.print_warning(f"mount[{self.subpath}]")
        sys_common.mount_to_server(self.uart, f"{self.subpath}")
        # step5 串口运行mixer pipeline
        if self.case_name != "show_perf_dualos":
            logger.print_warning("run mixer case")
            telnetmixer = Client(self.case_name, "telnet", "telnetmixer")
            mixerthread = MixerThread(telnetmixer)
            mixerthread.start()
        # step6 telnet cd 到mount目录，并运行show_interrupts.sh脚本
        logger.print_warning("connect telent && run case")
        telnet0 = Client(self.case_name, "telnet", "telnet0")
        time.sleep(5)
        cmd = "cd /mnt/;mkdir -p out/Cpu;"
        telnet0.write(cmd)
        logger.print_warning(f"case name:{self.case_name}")
        time.sleep(3)
        if self.case_name == "show_perf_dualos":
            logger.print_warning("cat dualos perf")
            cmd = "echo cli perf > /proc/dualos/rtos;echo cli perf --dump "/mnt/out/Cpu/perf.bin" > /proc/dualos/rtos"
            telnet0.write(cmd)
            time.sleep(3)
            cmd = "echo cli taskstat  > /proc/dualos/rtos; cat /proc/dualos/log > out/Cpu/rtos_task.txt"
            telnet0.write(cmd)
        else
            cmd = "./Suite/Cpu/resource/perf record -e cpu-clock -g -o /mnt/out/Cpu/sys.perf; ./Suite/Cpu/resource/perf script -i /mnt/out/Cpu/sys.perf > /mnt/out/Cpu/sys_perf.bin"
            telnet0.write(cmd)
        loopcnt = 0
        while loopcnt <= 30:
            time.sleep(1)
            # readresult, data = telnet0.read()
            loopcnt += 1
            # print(f"telnet read data:{data}")
        # step7 从mount 目录将原始数据和最终结果保存至指定目录，为了后续自动化展示结果
        logger.print_warning("read result")
        if self.case_name != "show_perf_dualos":
            mixerthread.join()
        telnet0.close()
        self.uart.close()
        # step8 切换到purelinux
        result = self.switch_os("purelinux")
        if result == 255:
            logger.print_warning(f"caseName[{self.case_name}] run done!")
            return 255
        return 0
