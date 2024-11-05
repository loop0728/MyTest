"""dts case"""
import os
import mmap
import struct
from sysapp_client import SysappClient
from suite.common.sysapp_common_logger import logger
import suite.common.sysapp_common_utils as sys_common
from suite.common.sysapp_common_device_opts import SysappDeviceOpts
from suite.common.sysapp_common_reboot_opts import SysappRebootOpts
from suite.bsp.common.sysapp_bsp_storage import SysappBspStorage
from suite.bsp.common.sysapp_bsp_image_ops import SysappBspImageOps
import suite.bsp.common.sysapp_bsp_image_ops as image_ops

class SysappBspDtsOps(SysappBspImageOps):
    """Bsp Dts Ops Case

    Attributes:
            uart_name (handle): case uart handle
            flash_handle:flash handle
    """
    def __init__(self, uart_name,flash_handle):
        """
        init func

        Args:
            uart_name: uart name
            flash_handle:flash handle
        """
        self.uart_dts=None
        if not isinstance(uart_name,SysappClient):
            raise TypeError(f"{uart_name} parameters must be SysappClient ")

        if uart_name.is_open is True:
            self.uart_dts = uart_name
        else:
            raise ValueError("uart_name.is_open must be True ")

        if not isinstance(flash_handle,SysappBspStorage):
            raise TypeError(f"{flash_handle} parameters must be SysappBspStorage ")
        super().__init__(self.uart_dts, flash_handle)



    def check_dts_lvalue(self,nodename,key,line_number=None):
        """
        check_dts_lvalue.
        Args:
            - nodename: The nodeName you want to check
            - key: The key you want to check in the nodename,
                    this param must be mutable, default is []
            - line_number : the line number about the node and key,
            Example: If dts file has following nodes
                my_node {
                    compatible = "sstar,csi";
                    #clock-cells = <0x00>;
                    clock-frequency = <0x16e3600>;
                    phandle = <0x86>;
                };

            if you want to check my_node existence or not
            just do this: check_dts_lvalue("my_node","",)

            if you want to check my_node:phandle existence or not
            just do this: check_dts_lvalue("my_node","phandle",)
        Returns:  0 success;  -1 fail; -2 nodename do not exsit; -3 key do not exsit
        """
        if not os.path.exists(self.dts_path):
            logger.error(f"{self.dts_path} is not exist")
            return -1
        with open(self.dts_path, 'r') as file:
            content = file.readlines()

        start_line = None
        end_line = None
        for i, line in enumerate(content):
            if line.strip().startswith(nodename):
                start_line = i
            elif start_line is not None and line.strip().startswith('}'):
                end_line = i
                break

        if start_line is not None and end_line is not None:
            logger.info(f"{nodename} found,Radius {start_line} : {end_line}")
            if isinstance(line_number, (list, dict, set)):
                line_number.append(start_line)
                line_number.append(end_line)
            if key == "":
                return 0

            found_key = False
            for i in range(start_line, end_line):
                if key in content[i]:
                    found_key=True
                    if isinstance(line_number, (list, dict, set)):
                        line_number.append(i)
                    logger.info(f"{key} found,line num {i}")
            if found_key is False:
                logger.warning(f"key '{key}' not found in new.dts")
                return -3
            return 0
        else:
            logger.warning(f"nodename '{nodename}' not found in new.dts")
            return -2

    def get_dts_rvalue(self,nodename,key,value):
        """
        check node or item existence or not in the dts file
        Args:
            - nodename: The nodeName you want to get the dts value
            - key: The key you want to get in the nodename,
            - value : the rvalue about the node and Key,this param must be mutable
            Example: If dts file has following nodes
                my_node {
                    compatible = "sstar,csi";
                    #clock-cells = <0x00>;
                    clock-frequency = <0x16e3600>;
                    phandle = <0x86>;
                };
            if you want to get my_node,just do this:
            value=[]
            get_dts_rvalue("my_node","",value)

            if you want to get my_node:phandle just do this:
            value=[]
            get_dts_rvalue("my_node","phandle",value)
        Return: 0 success;  -1 fail; -2 nodename do not exsit; -3 key do not exsit
        """
        list_num = []
        ret=self.check_dts_lvalue(nodename,key,list_num)
        if ret != 0:
            logger.error("check_dts_lvalue failed to execute")
            return ret

        try:
            with open(self.dts_path, 'r') as file:
                content = file.readlines()

            if key != "":
                value.append(content[list_num[2]].split("=")[1].strip()[:-1])
            else:
                for file_num in range(list_num[0],list_num[1]):
                    value.append(content[file_num].strip()[:-1])
            return 0
        except Exception as e:
            logger.error(f"with open func an error occurred: {str(e)}")
            return -1


    def add_dts_lvalue(self,nodename,key,value):
        """
        add item under NodeName
        Args:
            - NodeName: The nodeName you want to add into
            - Key: The item's left value
            - value : The item's right value
            Example: If dts file has following nodes
                my_node {
                    compatible = "sstar,csi";
                    #clock-cells = <0x00>;
                    clock-frequency = <0x16e3600>;
                    phandle = <0x86>;
                };

            if you want to add aaa=<ddd>; into  my_node
            just do this: add_dts_lvalue("my_node","aaa","ddd")

        Return: 0 success;  -1 fail; -2  Key already exists in file
        """
        list_num = []
        ret=self.check_dts_lvalue(nodename,key,list_num)
        if ret == 0:
            logger.warning(f"key '{key}' already exists")
            return -2
        elif ret < 0 and ret >= -2:
            logger.error("check_dts_lvalue failed to execute")
            return -1
        try:
            with open(self.dts_path, 'r') as file:
                content = file.readlines()
                info_empty_num=len(content[list_num[0]+1]) - len(content[list_num[0]+1].lstrip())
                if value == "":
                    node_info=f"{' ' * info_empty_num*4}{key};\n"
                else:
                    node_info=f"{' ' * info_empty_num*4}{key}=<{value}>;\n"
                content.insert(list_num[1],node_info)

            with open(self.dts_path, 'w') as file:
                file.writelines(content)
                logger.info(f" '{key}' successfully add under {nodename}")
                return 0

        except Exception as e:
            logger.error(f"with open func an error occurred: {str(e)}")
            return -1


    def delete_dts_lvalue(self,nodename,key):
        """
        delete item under NodeName
        Args:
            - NodeName: The nodeName you want to delete into
            - Key: The item's you want to delete
            Example: If dts file has following nodes
                my_node {
                    compatible = "sstar,csi";
                    #clock-cells = <0x00>;
                    clock-frequency = <0x16e3600>;
                    phandle = <0x86>;
                };

            if you want to delete phandle = <0x86>; into  my_node
            just do this: delete_dts_lvalue("my_node","phandle")

        Return: 0 success;  -1 fail; -2  Key not exists in file
        """
        list_num = []
        ret=self.check_dts_lvalue(nodename,key,list_num)
        if ret != 0:
            logger.warning(f"key '{key}' not exists")
            return -2

        try:
            with open(self.dts_path, 'r') as file:
                content = file.readlines()
                del content[list_num[2]]

            with open(self.dts_path, 'w') as file:
                file.writelines(content)
                logger.info(f" '{key}' successfully delete under {nodename}")
                return 0
        except Exception as e:
            logger.error(f"with open func an error occurred: {str(e)}")
            return -1

    def replace_dts_value(self,nodename,key,value):
        """
        Replace the value of the corresponding key under nodename in dts with value.
        Args:
            - NodeName: Node name.
            - Key: The lvalue of the property to be modified (the property name of the node name).
            - value: The Rvalue of key.
        Return:  0 success   -1 fail.
        Notes: You cannot replace an item with an rvalue of a string.
        """
        list_num = []
        ret=self.check_dts_lvalue(nodename,key,list_num)
        if ret != 0:
            logger.warning(f"key '{key}' not exists")
            return -2

        try:
            with open(self.dts_path, 'r') as file:
                content = file.readlines()
                parts = content[list_num[2]].split("=")
                if len(parts) == 2:
                    left = parts[0]
                    right = parts[1]
                    if "<" in right:
                        new_line = f"{left}= <{value}>;\n"
                    elif "\"" in right:
                        new_line = f"{left}= \"{value}\";\n"
                    content[list_num[2]] = new_line

            with open(self.dts_path, 'w') as file:
                file.writelines(content)
                logger.info(f"Successfully replaced {key} with {value} in new.dts")
                return 0
        except Exception as e:
            logger.error(f"with open func an error occurred: {str(e)}")
            return -1


    def repalce_image_dts(self):
        """
        Replace dtb in iamge.
        Args:
            na
        Return:  0 success   -1 fail.
        Notes: You cannot replace an item with an rvalue of a string.
        """
        base_dir=os.path.dirname(self.dts_path)
        dtb_dir=base_dir+"/new.dtb"
        dtb_dts_to_dtb_para=["-I dts","-O dtb",f"-o {dtb_dir}",f"{self.dts_path}"]
        ret=self.run_image_cmd("dtc",dtb_dts_to_dtb_para,[])
        if ret is False:
            logger.error("run_image_cmd failed to execute")
            return ret

        #1、 替换 dtb, 需要 Image  dtb
        with open(dtb_dir, "rb") as file:
            file_content = file.read()
            file_size = len(file_content)
            if file_size > (128*1024):
                logger.error( f"DTB size 0x{file_size} too big to fit in 128K limit!!")
                return False


        imagefd=os.open(self.image_path,os.O_RDWR)
        fmap=mmap.mmap(imagefd,0)
        name="#MS_DTB#"
        offset=fmap.find(name.encode("utf-8"))
        if offset >=0:
            logger.info(f"offset:0x{offset}" )
            logger.info(f"  size:0x{file_size}")
            fmap.seek(offset + 8, os.SEEK_SET)
            fmap.write(struct.pack('<I', file_size))
            fmap.seek(offset + 16, os.SEEK_SET)
            fmap.write(file_content)
            logger.info("replace dtb file successfully")
        else:
            fmap.close()
            os.close(imagefd)
            logger.error(f"can not found {name}")
            return False

        unfdtname="#UNFDT_#"
        fmap=mmap.mmap(imagefd,0)
        offset=fmap.find(unfdtname.encode("utf-8"))
        if offset >=0:
            logger.info(f"UNFDT offset:0x{offset}")
            logger.info(f"  size:0x{file_size}")

            dtb_to_fdt_para=[dtb_dir,f"{base_dir}/unfdt.bin"]
            ret=self.run_image_cmd("dtb2unfdt",dtb_to_fdt_para,[])
            if ret is False:
                logger.error("run_image_cmd failed to execute")
                return False

            with open(f"{base_dir}/unfdt.bin", "rb") as file:
                file_content = file.read()
                file_size = len(file_content)
                if file_size > (192*1024):
                    logger.error( f"DTB size 0x{file_size} too big to fit in 192K limit!!")
                    return False

            fmap.seek(offset + 8, os.SEEK_SET)
            fmap.write(file_content)
            logger.info("replace unfdt file successfully")
        else:
            logger.warning("do not find unfdt file")
        fmap.close()
        os.close(imagefd)
        return True


    def bsp_dts_ota_pack(self,image_name):
        """
        ota packages kernel partitions.
        Args:
            -image_name:image name you want to upgrade. KERNEL or RTOS
        Return:  True success   False fail.
        Notes: The file is stored in ./resource/replace_dtb.

        """
        base_image_path=os.path.dirname(self.image_path)
        kernel_info=[]
        result, partition_list=SysappDeviceOpts.get_mtdparts(self.uart_dts)
        if result is False:
            logger.error("get_mtdparts failed to get board type")
            return False

        for sigel in partition_list:
            if sigel[1] == image_name:
                kernel_info.append(f"/dev/mtd{sigel[0]}")
                kernel_info.append(f"0x{sigel[2]}")

        if self.image_compress_type is None:
            ret=self.get_image_compress_type(f"{self.image_path}_real")
            if ret is False:
                logger.error("get_image_compress_type failed to execute")
                return False

        if self.image_compress_type == "none":
            pass
        elif self.image_compress_type == "lzma":   # xz compression
            image_name=f"{image_name}.xz"
        elif self.image_compress_type == "lzma2":   # sz compression
            image_name=f"{image_name}.ssz"
        else:
            logger.error(f" do not support this {self.image_compress_type} type")
            return -1

        ota_para=[f"-c {base_image_path}/SStarOta.bin"]
        self.otapack(ota_para)
        ota_para_2=[f'-s {base_image_path}/{image_name}',
                    f'-d {kernel_info[0]}',
                    f'-t {kernel_info[1]}',
                    ' --default-mask -m 0 --block-update -l kernel'
                    f' -a {base_image_path}/SStarOta.bin']

        ret=self.otapack(ota_para_2)
        if ret is False:
            logger.error("cmd_run_on_board+  failed to execute")
            return -1
        return 0

    def bsp_dts_ota_upgrade(self,image_name):
        """
        ota packages kernel partitions.
        Args:
            -image_name:image name you want to upgrade
        Return:  True success   False fail.

        """
        if image_name == "KERNEL":
            path="replace_dtb"
        elif image_name == "RTOS":
            path="rtos_replace_sys"
        else:
            logger.error("do not support")
            return False

        cmd=f"cp {self.tool_dir[0]}/{path}/SStarOta.bin /mnt/SStarOta.bin"
        ret, _ =sys_common.write_and_match_keyword(self.uart_dts,cmd,"/ #",False,9999,999)
        if ret is False:
            logger.error(f"{cmd} failed to execute")

        cmd=f"{self.tool_dir[0]}/otaunpack -r /mnt/SStarOta.bin"
        ret, _ =sys_common.write_and_match_keyword(
            self.uart_dts,cmd,"Process exited with status",False,9999,999)
        if ret is False:
            logger.error(f"{cmd} failed to execute")
            return False

        cmd="rm -rf /mnt/SStarOta.bin"
        ret, _ =sys_common.write_and_match_keyword(self.uart_dts,cmd,"/ #",False,9999,999)


        if self.image_compress_type == "none":
            pass
        elif self.image_compress_type == "lzma":   # xz compression
            image_name=f"{self.image_path}.xz"
        elif self.image_compress_type == "lzma2":   # sz compression
            image_name=f"{self.image_path}.ssz"
        else:
            logger.error(f" do not support this {self.image_compress_type} type")
            return False

        file_size = hex(os.path.getsize(image_name))
        cmd_change_uboot_env="/etc/fw_setenv kernel_file_size " +str(file_size)
        ret, _ =sys_common.write_and_match_keyword(self.uart_dts,cmd_change_uboot_env,"/ #")
        if ret is False:
            logger.error(f"{cmd_change_uboot_env} failed to execute")
            return False

        ret=SysappRebootOpts.reboot_to_kernel(self.uart_dts)
        if ret is False:
            logger.error("reboot failed to execute")
            return False
        return True

    def image_restore(self,image_name):
        """
        image restore.
        Args:
            -image_name:image name you want to upgrade
        Return:  True success   False fail.

        """
        logger.info(f"ops:{image_name}")
        if self.image_compress_type is None:
            ret=self.get_image_compress_type(f"{self.image_path}_real")
            if ret is False:
                logger.error("get_image_compress_type failed to execute")
                return False

        if self.image_compress_type == "none":
            image_full_name=self.image_path
        elif self.image_compress_type == "lzma":   # xz compression
            image_full_name=f"{self.image_path}.xz"
        elif self.image_compress_type == "lzma2":   # sz compression
            image_full_name=f"{self.image_path}.ssz"
        else:
            logger.error(f" do not support this {self.image_compress_type} type")
            return False

        cmd_run_on_board="rm -rf "+image_full_name
        ret=image_ops.server_run_shell_command(cmd_run_on_board,)
        if ret is False:
            logger.error(f"{cmd_run_on_board} failed to execute")
            return False

        cmd_run_on_board="cp "+self.image_path +"_restore "+image_full_name+" -f"
        ret=image_ops.server_run_shell_command(cmd_run_on_board,)
        if ret is False:
            logger.error(f"{cmd_run_on_board} failed to execute")

        ret=self.bsp_dts_ota_pack("KERNEL")
        if ret is False:
            logger.error("server_rtos_ota_pack failed")
            return False
        ret=self.bsp_dts_ota_upgrade("KERNEL")
        if ret is False:
            logger.error("server_rtos_ota_upgrade failed")
            return False

        return True

    def bsp_dts_get_image(self,image_name):
        """
        get_image.
        Args:
            -image_name:image name you want to upgrade
        Return:  True success   False fail.

        """
        ret=self.get_image(image_name)
        if ret is False:
            logger.error("get_image failed")
            return False
        ret=self.get_kernel_from_kernel_image()
        if ret is False:
            logger.error("get_kernel_from_kernel_image failed")
            return False
        ret=self.uncompress_image()
        if ret is False:
            logger.error("uncompress_image failed")
            return False
        ret=self.get_dtb_from_kernel()
        if ret is False:
            logger.error("get_dtb_from_kernel failed")
            return False
        return True

    def bsp_dts_genarate_image(self,image_name):
        """
        genarate image.
        Args:
            -image_name:image name you want to upgrade
        Return:  True success   False fail.

        """
        ret=self.repalce_image_dts()
        if ret is False:
            logger.error("get_image failed")
            return False
        ret=self.genarate_image(image_name)
        if ret is False:
            logger.error("get_image failed")
            return False
        return True
