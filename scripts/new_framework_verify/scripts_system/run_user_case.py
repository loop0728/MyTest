import sys
from PythonScripts.logger import logger
from Common.error_codes import event_handlers

class RunUserCase():
    def __init__(self, param_list=[]):
        if len(param_list) < 2:
            logger.print_error("run_user_case param num less 2")
            return 255
        self.case_run_cnt = 1
        self.module_path_name = param_list[1]
        self.case_name = param_list[2]
        self.module_path = "/".join(self.module_path_name.split("/")[:-1])
        logger.print_info("module_path_name: {}".format(self.module_path_name))
        logger.print_info("case_name: {}".format(self.case_name))

    def parase_case_run(self) -> int:
        result = 255
        calss_obj = ''
        module_name = self.module_path_name.split("/")[-1].split(".")[0]
        logger.print_info("module_path: {}".format(self.module_path))
        logger.print_info("module_name: {}".format(module_name))

        sys.path.append(self.module_path)
        module = __import__(module_name)
        logger.print_info("case_name:{}".format(self.case_name))
        calss_obj = getattr(module, module_name) #get mode class
        if  self.case_name != 'NULL' and  self.case_name != '' and self.case_name != "help":
            instance = calss_obj(self.case_name, self.case_run_cnt, self.module_path_name)#use class creat one instance
            if not instance:
                logger.print_error("create instance fail!\n")
        else:
            instance = calss_obj(module_name, self.case_run_cnt, self.module_path_name)#use class creat one instance
            if not instance:
                logger.print_error("create instance fail!\n")
            instance.runcase_help()
            return 0
        try:
            result = instance.runcase()
        except Exception as e:
            logger.print_error(e)
        self.print_run_result(result)
        if result != 0:
            self.exception_handling(result)
        return result

    def print_run_result(self, result):
        if result:
            logger.print_warning("[AutoTest][{}][fail][{}][run_cnt:{}]".format(self.case_name, result, self.case_run_cnt))
        else:
            logger.print_warning("[AutoTest][{}][pass][{}][run_cnt:{}]".format(self.case_name, result, self.case_run_cnt))

    def exception_handling(self, err_code):
        handler = event_handlers.get(err_code)
        if handler:
            handler()
        else:
            logger.print_warning("Unknown error code.")
        return err_code


if __name__ == "__main__":
   run_case_handle = RunUserCase(sys.argv)
   ret = run_case_handle.parase_case_run()
   sys.exit(ret)