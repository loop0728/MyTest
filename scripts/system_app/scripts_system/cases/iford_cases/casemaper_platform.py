""" iford case maper"""
from run_env.casemaper_base import SysappCaseMaperBase

class SysappCaseMaperPlatform(SysappCaseMaperBase):
    """ SysappCaseMaperPlatform """
    def __init__(self):
        SysappCaseMaperBase.__init__(self)
        # 请确保添加的case名与mixer/ptree中所对应的文件名一致 !!!
        self.lists = {
            "0x01": ["1snr_3m15p_ipu_disp_ptree", "1snr_4m15p_ipu_vdf_ptree",
                "1snr_4m30p_ipu_ptree", "1snr_8m15p_ptree"],
            "0x02": ["1snr_8m24p_ive", "1snr_4m30p_ipu_vdf_disp", "1snr_8m24p_ipu_pet_det_disp",
                "1snr_4m20p_ipu_vdf", "1snr_8m24p_ipu_vdf", "1snr_8m24p_ipu", "1snr_8m24p_ldc",
                "1snr_8m24p_hdr", "1snr_4m30p_hdr_multiprocess"],
            "0x04": ["2snr_4m15p_ipu_realtime", "2snr_4m15p_realtime_ipu_multiprocess"],
            "0x08": ["1snr_4m20p_ipu_vdf", "1snr_8m24p_ipu_vdf", "1snr_isp_scl_venc"]
        }
