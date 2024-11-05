"""dts case"""
import os
import subprocess
import mmap
from sysapp_client import SysappClient
from suite.common.sysapp_common_logger import logger
from suite.common.sysapp_common_device_opts import SysappDeviceOpts
from suite.bsp.common.sysapp_bsp_storage import SysappBspStorage
from cases.platform.bsp.common.sysapp_bsp_dts_ops_var import DTS_OPS_TOOL_DIR


def server_run_shell_command(command,cmd_stdout = None):
    """ run_shell_command

    Attributes:
            uart_command: cmd you wnnt to run
            cmd_stdout:cmd out
    """
    if command:
        logger.info(f"command: {command}")
    else:
        logger.error("command is empty")
        return False
    cmd_result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if cmd_result.returncode != 0:
        logger.error(cmd_result.stderr)
        return False
    else:
        logger.info(cmd_result.stdout.decode("utf-8"))
        if cmd_stdout is not None:
            cmd_stdout.append(cmd_result.stdout.decode("utf-8").rstrip("\n"))
            return True
        elif cmd_stdout is None:
            return True
        else:
            logger.error("wrong type of cmd_stdout")
            return False

def remove_image_header(image_in_name,file_header_size,image_out_name):
    """
    remove image header
    Args:
        - image_in_name: input filename
        - file_header_size: header size.
        - image_out_name: output filename
    Returns: True success   False fail.
    """

    # file_header_size=64
    if not os.path.exists(image_in_name):
        logger.error(f"{image_in_name} is not exists")
        return False
    try:
        with open(image_in_name, 'rb') as file:
            file.seek(file_header_size)
            remaining_data = file.read()

        with open(image_out_name, 'wb') as file:
            file.write(remaining_data)
    except FileNotFoundError:
        logger.error("File not found.")
        return False
    except (IOError, OSError) as e:
        logger.error(f"An error occurred: {e}")
        return False
    return True

class SysappBspImageOps():
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
        self.uart=None
        self.storage=None
        if not isinstance(uart_name,SysappClient):
            raise TypeError(f"{uart_name} parameters must be SysappClient ")

        if uart_name.is_open is True:
            self.uart = uart_name
        else:
            raise ValueError("uart_name.is_open must be True ")

        if not isinstance(flash_handle,SysappBspStorage):
            raise TypeError(f"{flash_handle} parameters must be SysappBspStorage ")
        self.storage=flash_handle
        self.image_path=None
        self.dts_path=None
        self.tool_dir=DTS_OPS_TOOL_DIR
        self.image_compress_type=None

    def get_image_compress_type(self,image_name):
        """
        get image compress type.
        Args:
            - image_name: image name.
        Returns: True success   False fail.
        Notes:  lzma2 -> sz
                lz4 -> lz4
                lzma -> xz
                none -> none
        """

        image_compress_type=[[0,"none"],
                            [1,"gzip"],
                            [2,"bzip2"],
                            [3,"lzma"],
                            [4,"lzo"],
                            [5,"lz4"],
                            [6,"zstd"],
                            [7,"reserved1"],
                            [8,"reserved2"],
                            [9,"mz"],
                            [10,"xip"],
                            [11,"lzma2"],
                            [12,"max"]]

        try:
            with open(image_name, 'rb') as file:
                bytes_data = file.read(64)
                compress_index=bytes_data[31]
        except FileNotFoundError:
            logger.error("File not found.")
            return False
        except (IOError, OSError) as e:
            logger.error(f"An error occurred: {e}")
            return False

        if  compress_index >= len(image_compress_type):
            logger.error(f"wrong compress type: {compress_index}")
            return False
        else:
            for info in image_compress_type:
                if info[0] == compress_index:
                    self.image_compress_type=info[1]
        return True


    def run_image_cmd(self,cmd,parameters,cmd_out):
        """
        run image cmd
        Args:
            - cmd:The default cmd uses the path:self.tool_dir[1],You can also specify your own path
            - Parameters: cmd Parameters.
            - cmd_out: cmd output,can be [] if you do not nedd output
        Returns: True success   False fail.
        """
        cmd_image=cmd
        if "/" not in cmd:
            cmd_image = self.tool_dir[1]+"/"+cmd

        if not os.path.exists(cmd_image):
            logger.error(f"{cmd_image} is not exists")
            return False

        if parameters:
            logger.info(f"{cmd} {parameters}")
        else:
            logger.error(f"{cmd} parameters is empty")
            return False

        for param in parameters:
            cmd_image=cmd_image+" "+param
        ret=server_run_shell_command(cmd_image,cmd_out)
        if ret is False:
            logger.error(f"{cmd_image} failed to execute")
            return False

        return True

    def otapack(self,parameters):
        """
        otapack
        Args:
            - Parameters: cmd Parameters.
        Returns: True success   False fail.
        """
        ret=self.run_image_cmd("otapack",parameters,[])
        if ret is False:
            logger.error("otapack failed to execute")
            return False
        return True


    def sz_uncompress(self,image_in_name,image_out_name):
        """
        Description: Unzip the sz file.
        Args:
            - image_in_name: input filename
            - image_out_name: output filename
        Returns: True success   False fail.
        """
        if not os.path.exists(image_in_name):
            logger.error(f"{image_in_name} is not exists")
            return -1
        directory, filename_with_extension = os.path.split(image_out_name)
        filename, _ = os.path.splitext(filename_with_extension)

        temp_xz_file_name=directory+"/"+filename+".xz"

        szrestore_para=[image_in_name,temp_xz_file_name]
        ret=self.run_image_cmd("szrestore",szrestore_para,[])
        if ret is False:
            logger.error("szdec failed to execute")
            return False
        szdec_para=[temp_xz_file_name,image_out_name]
        ret=self.run_image_cmd("szdec",szdec_para,[])
        if ret is False:
            logger.error("szdec failed to execute")
            return False
        logger.info("sz_uncompress successful ")
        return True


    def xz_uncompress(self,image_in_name,image_out_name):
        """
        Description: Unzip the xz file.
        Args:
            - image_in_name: input filename
            - image_out_name: output filename
        Returns: True success   False fail.
        """
        if not os.path.exists(image_in_name):
            logger.error(f"{image_in_name} is not exists")
            return False
        xz_uncopress_para=["-d","-f","-k",image_in_name,"-c",">",image_out_name]
        ret=self.run_image_cmd("/usr/bin/xz",xz_uncopress_para,[])
        if ret is False:
            logger.error("/usr/bin/xz failed to execute")
            return False
        logger.info("xz_uncompress successful ")
        return True


    def mkimage(self,image_in_name,parameters,image_out_name):
        """
        Description: image add file header.
        Args:
            - image_in_name: input filename
            - Parameters: mkiamge Parameters
            - image_out_name: output filename
        Returns: True success   False fail.
        """
        if not os.path.exists(image_in_name):
            logger.error(f"{image_in_name} is not exists")
            return False
        if parameters:
            logger.info(f"mkimage {parameters}")
        else:
            logger.error(f"{parameters} is empty")
            return False
        parameters.append(f"-d {image_in_name}")
        parameters.append(f"{image_out_name}")
        ret=self.run_image_cmd("mkimage",parameters,[])
        if ret is False:
            logger.error("mkimage failed to execute")
            return False
        return True


    def sz_compress(self,image_in_name,parameters):
        """
        Description: sz compressed file.
        Args:
            - image_in_name: input filename
            - image_out_name: output filename
        Returns: True success   False fail.
        """
        if not os.path.exists(image_in_name):
            logger.error(f"{image_in_name} is not exists")
            return False

        if parameters:
            logger.info(f"sz {parameters}")
        else:
            logger.error(f"{parameters} is empty")
            return False

        parameters.append(image_in_name)

        ret=self.run_image_cmd("sz",parameters,[])
        if ret is False:
            logger.error("sz failed to execute")
            return False
        return True


    def szdec(self,parameters,cmd_result):
        """
        Description: szdec cmd.
        Args:
            - Parameters: mkiamge Parameters
            - cmd_result: result of command:szdec
        Returns: True success   False fail.
        """
        if parameters:
            logger.info(f"szdec {parameters}")
        else:
            logger.error(f"{parameters} is empty")
            return False

        if not os.path.exists(parameters[0]) or not os.path.exists(parameters[1]):
            logger.error(f"{parameters[0]} or {parameters[1]} is not exists")
            return False

        ret=self.run_image_cmd("szdec",parameters,cmd_result)
        if ret is False:
            logger.error("sz failed to execute")
            return False
        return True


    def szsplit(self,image_in_name,image_out_name):
        """
        Description: szsplit cmd.
        Args:
            - image_in_name: input filename
            - image_out_name: output filename
        Returns: True success   False fail.
        """
        if not os.path.exists(image_in_name):
            logger.error(f"{image_in_name} is not exists")
            return False
        parameters=[image_in_name,image_out_name]
        ret=self.run_image_cmd("szsplit",parameters,[])
        if ret is False:
            logger.error("sz failed to execute")
            return False
        return True



    def xz_compress(self,image_in_name,parameters):
        """
        Description:  xz compressed file.
        Args:
            - image_in_name: input filename
            - Parameters: xz Parameters
        Returns: True success   False fail.
        """
        if not os.path.exists(image_in_name):
            logger.error(f"{image_in_name} is not exists")
            return False
        parameters.append(image_in_name)
        ret=self.run_image_cmd("/usr/bin/xz",parameters,[])
        if ret is False:
            logger.error("xz failed to execute")
            return False
        return True



    def generate_image_sz(self,image_in_name):
        """
        Description: Make the compressed file ssz.
        Args:
            - image_in_name: input filename
        Returns: True success   False fail.
        """
        file_size_max="64MiB"
        cmd_out=[""]

        if not os.path.exists(image_in_name):
            logger.error(f"{image_in_name} is not exists")
            return False

        directory, filename_with_extension = os.path.split(image_in_name)
        filename, _ = os.path.splitext(filename_with_extension)
        first_sz_para=["-z","-f","-k",
                        "--check=crc32",
                        "--lzma2=dict=4KiB",
                        f"--block-list={file_size_max}",
                        f"--block-size={file_size_max}",
                        "--threads=4"]
        # creat u_rtos_image.xz
        ret=self.sz_compress(image_in_name,first_sz_para)
        if ret is False:
            logger.error("sz_compress failed to execute")
            return False
        szdec_para=[f"{image_in_name}.xz",f"{image_in_name}","split_block=4"]
        ret=self.szdec(szdec_para,cmd_out)
        if ret is False:
            logger.error("szdec failed to execute")
            return False
        second_sz_para=["-z","-f","-k",
                        "--check=crc32",
                        "--lzma2=dict=4KiB",
                        f"--block-list={cmd_out[1]}{file_size_max}",
                        f"--block-size={file_size_max}","--threads=4"]
        ret=self.sz_compress(f"{image_in_name}",second_sz_para)
        if ret is False:
            logger.error("sz_compress failed to execute")
            return False
        ret=self.szsplit(f"{image_in_name}.xz",f"{directory}/{filename}.sz")
        if ret is False:
            logger.error("szsplit failed to execute")
            return False

        logger.info(f"genarate  {directory}/{filename}.sz successfully")
        return True

    def generate_image_xz(self,image_in_name):
        """
        Description: Make the compressed file xz.
        Args:
            - image_in_name: input filename
        Returns: True success   False fail.
        """
        if not os.path.exists(image_in_name):
            logger.error(f"{image_in_name} is not exists")
            return False
        xz_para =["-z", "-k", "-f"]
        ret=self.xz_compress(image_in_name,xz_para)
        if ret is False:
            logger.error("szsplit failed to execute")
            return False

        logger.info(f"genarate  {image_in_name}.xz successfully")
        return True


    def get_image(self,image_name):
        """
        Obtain the Image and dts from the kernel partition.
        Args:
            - image_name: image partition name
        Returns: True success   False fail.
        """
        if image_name == "KERNEL":
            path="replace_dtb"
        elif image_name == "RTOS":
            path="rtos_replace_sys"
        else:
            logger.error("do not support")
            return False

        image_path=f"{self.tool_dir[1]}/{path}"
        self.image_path=f"{image_path}/{image_name}"

        if not os.path.exists(image_path):
            os.mkdir(image_path)
        # 删除上次中间文件
        cmd_rm_temp_file=f"rm {image_path}/* -rf"
        ret=server_run_shell_command(cmd_rm_temp_file, )
        if ret is False:
            logger.error(f"{cmd_rm_temp_file} failed to execute")
            return False

        image_info=[]
        result, partition_list=SysappDeviceOpts.get_mtdparts(self.uart)
        if result is False:
            logger.error("get_mtdparts failed to get board type")
            return False

        for sigel in partition_list:
            if sigel[1] == image_name:
                image_info.append(f"/dev/mtd{sigel[0]}")
                image_info.append(f"0x{sigel[2]}")

        if image_info:
            logger.info(f"{image_name} found dev/mtd{image_info[0]}  size: {image_info[1]}")
        else:
            logger.error(f"{image_name} not found")
            return False

        self.storage.dump(image_info[0],image_info[1],f"{self.tool_dir[0]}/{path}/{image_name}")
        cmd_creat_kernel_restore = f"cp {self.image_path}"+f" {self.image_path}"+"_restore"
        ret=server_run_shell_command(cmd_creat_kernel_restore,)
        if ret is False:
            logger.error(f"{cmd_creat_kernel_restore} failed to execute")
            return False
        return True

    def get_kernel_from_kernel_image(self):
        """
        get real kernel from kernel image.
        Args:
            na
        Returns: True success   False fail.
        """
        with open(f"{self.image_path}", 'rb') as file:
            file.seek(12,0)
            bytes_data = file.read(4)
            image_ssz_size = int.from_bytes(bytes_data, 'big')
            logger.info(f"kernel size:{str(image_ssz_size)}")
            file.seek(0)
            full_image = file.read(image_ssz_size+64)

        cmd_creat_kernel_restore = f"rm {self.image_path}"
        ret=server_run_shell_command(cmd_creat_kernel_restore,)
        if ret is False:
            logger.error(f"{cmd_creat_kernel_restore} failed to execute")
            return False

        with open(f"{self.image_path}_real", 'wb') as file:
            file.write(full_image)


        return True

    def uncompress_image(self):
        """
        uncompress image.
        Args:
            na
        Returns: True success   False fail.
        """
        if self.image_compress_type is None:
            ret=self.get_image_compress_type(f"{self.image_path}_real")
            if ret is False:
                logger.error("get_image_compress_type failed to execute")
                return False

        if self.image_compress_type == "none":
            logger.info(f"{self.image_path}"+f"compression_type:{self.image_compress_type}")

        elif self.image_compress_type == "lzma":   # xz compression
            # create rtos.ssz
            temp_source_name=self.image_path+"_real"
            temp_target_name=self.image_path+".xz"
            ret=remove_image_header(temp_source_name,64,temp_target_name)
            if ret is False:
                logger.error("remove_image_header failed to execute")

            temp_target_name=self.image_path
            temp_source_name=self.image_path+".xz"
            ret=self.xz_uncompress(temp_source_name,temp_target_name)
            if ret is False:
                logger.error("xz_uncompress failed to execute")
                return ret
        elif self.image_compress_type == "lzma2":   # sz compression
            # create rtos.ssz
            temp_source_name=self.image_path+"_real"
            temp_target_name=self.image_path+"u.ssz"
            ret=remove_image_header(temp_source_name,64,temp_target_name)
            if ret is False:
                logger.error("remove_image_header failed to execute")

            temp_target_name=self.image_path+"_u_uncompressed"
            temp_source_name=self.image_path+"u.ssz"
            ret=self.sz_uncompress(temp_source_name,temp_target_name)
            if ret is False:
                logger.error("sz_uncompress failed to execute")
                return ret
            temp_source_name=self.image_path+"_u_uncompressed"
            temp_target_name=self.image_path
            ret=remove_image_header(temp_source_name,64,temp_target_name)
            if ret is False:
                logger.error("remove_image_header failed to execute")
                return ret
        else:
            logger.error(f"unknown {self.image_compress_type} to do")
            return False

        return True

    def get_dtb_from_kernel(self):
        """
        get dtb from kernel.
        Args:
            na
        Returns: True success   False fail.
        """
        dtb_file=None
        # 从 Image 文件中拿到 dtb 文件的大小，读出 dtb
        imagefd=os.open(self.image_path,os.O_RDWR)
        fmap=mmap.mmap(imagefd,0)
        name="#MS_DTB#"
        offset=fmap.find(name.encode("utf-8"))
        if offset >=0:
            fmap.seek(offset + 20, os.SEEK_SET)
            bytes_data=fmap.read(4)
            dtb_size=int.from_bytes(bytes_data, 'big')
            logger.info(f"dtb size: {str(dtb_size)}")
            fmap.seek(offset + 16, os.SEEK_SET)
            dtb_file=fmap.read(dtb_size)
        fmap.close()
        os.close(imagefd)

        dts_base_dir=os.path.dirname(self.image_path)
        with open(f"{dts_base_dir}/old.dtb", 'wb') as file:
            file.write(dtb_file)

        # 将 dtb 文件转换为 dts 文件
        dtb_dtb_to_dtc_para=["-I dtb",
                            "-O dts",
                            f"-o {dts_base_dir}/old.dts",
                            f"{dts_base_dir}/old.dtb"]
        ret=self.run_image_cmd("dtc",dtb_dtb_to_dtc_para,[])
        if ret is False:
            logger.error("run_image_cmd failed to execute")
            return ret

        self.dts_path=f"{dts_base_dir}/new.dts"
        cmd_creat_newdts=f"cp {dts_base_dir}/old.dts {self.dts_path}"

        ret=server_run_shell_command(cmd_creat_newdts,)
        if ret is False:
            logger.error(f"{cmd_creat_newdts} failed to execute")
            return ret
        return True


    def genarate_image(self,image_name):
        """
        genarate image. include add header and compress.
        Args:
            - image_name: image you want to genarate. KERNEL or RTOS
        Return:  True success   False fail.
        Notes: You cannot replace an item with an rvalue of a string.
        """
        cmd_mkimage_name=(f"/usr/bin/strings -a -T binary {self.image_path}"
                        " | grep 'MVX' | grep 'LX'  | sed 's/\\*MVX/MVX/g' | cut -c 1-32")
        strings_result=[""]
        ret=server_run_shell_command(cmd_mkimage_name,strings_result)
        if ret is False:
            logger.error(f"{cmd_mkimage_name} failed to execute")
            return False
        else:
            imagename = strings_result[1].rstrip("\n")

        logger.info(f"ops image:{image_name}")

        if self.image_compress_type is None:
            ret=self.get_image_compress_type(f"{self.image_path}_real")
            if ret is False:
                logger.error("get_image_compress_type failed to execute")

        if self.image_compress_type == "none":
            logger.info(f"{{self.image_path}} compression_type:{self.image_compress_type}")

        elif self.image_compress_type == "lzma":   # xz compression
            # add header
            ret=self.generate_image_xz(f"{self.image_path}")
            if ret is False:
                logger.error("generate_image_xz failed to execute")
                return False
            first_para=["-A arm",
                        "-O linux",
                        f"-C {self.image_compress_type}",
                        "-a 0x20008000",
                        "-e 0x20008000",
                        f"-n {imagename}"]
            cmd_mkimage_name=f"mv {self.image_path}.xz {self.image_path}_temp.xz"
            ret=server_run_shell_command(cmd_mkimage_name,)
            self.mkimage(f"{self.image_path}_temp.xz",first_para,f"{self.image_path}.xz")
        elif self.image_compress_type == "lzma2":   # sz compression
            # add header
            first_para=["-A arm",
                        "-O linux",
                        "-C none",
                        "-a 0x20008000",
                        "-e 0x20008000",
                        f"-n {imagename}"]
            ret=self.mkimage(
                f"{self.image_path}",first_para,f"{self.image_path}_uncompressed_u")
            if ret is False:
                logger.error("mkimage failed to execute")
            ret=self.generate_image_sz(f"{self.image_path}_uncompressed_u")
            if ret is False:
                logger.error("generate_image_sz failed to execute")
                return False
            # add header
            logger.info(self.image_compress_type)
            second_para=["-A arm",
                                "-O linux",
                                f"-C {self.image_compress_type}",
                                "-a 0x20008000",
                                "-e 0x20007fc0",
                                f"-n {imagename}"]
            logger.info(second_para)
            ret=self.mkimage(
                f"{self.image_path}_uncompressed_u.sz",second_para,f"{self.image_path}.ssz")
            if ret is False:
                logger.error("mkimage failed to execute")
                return False
        else:
            logger.error(f"dont support uncompress type {self.image_compress_type}")
            return False
        return True
