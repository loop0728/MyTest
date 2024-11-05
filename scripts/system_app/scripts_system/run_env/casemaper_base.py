""" SysappCaseMaperBase version 0.0.1 """
class SysappCaseMaperBase:
    """ every chip have owen case stage, and need to get stage map to cases """

    def __init__(self):
        self.lists = {}

    def get_cases_from_stage(self, stage):
        """ get_cases_from_stage """
        return self.lists.get(stage, None)

    @staticmethod
    def find_matching_files(filelist, stagemaplist):
        """
        找出 filelist 中包含 stagemaplist 中任一字符串的完整文件路径。

        Args:
            filelist: 包含完整文件路径的列表。
            stagemaplist: 包含文件名部分的列表。

        Returns:
            包含匹配文件的列表。
        """
        outlist = []
        for file in filelist:
            for pattern in stagemaplist:
                if pattern in file:
                    outlist.append(file)
                    break  # 找到一个匹配就跳出内层循环
        return outlist
