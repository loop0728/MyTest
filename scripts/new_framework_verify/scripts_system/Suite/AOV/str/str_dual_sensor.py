from str import str_handle

class str_dual_sensor_handle(str_handle):
    def __init__(self, case_name, case_log_path, case_run_cnt=1, module_path_name='./'):
        super().__init__(case_name, case_log_path, case_run_cnt, module_path_name)
        self.cmd_aov_run               = "/customer/sample_code/bin/prog_aov_aov_demo dual_sensor -t -d"

