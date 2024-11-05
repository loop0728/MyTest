"""System UT common API."""
#!/usr/bin/python3
# -*- coding: utf-8 -*-

from suite.common.sysapp_common_logger import logger


def are_files_equal_line_by_line(file1, file2):
    """
    Are files equal line by line.

    Args:
        file1 (str): file1 path
        file2 (str): file2 path

    Returns:
        bool: result
    """
    with open(file1, "r", encoding="utf-8") as test_file1, open(
            file2, "r", encoding="utf-8"
    ) as test_file2:
        for line1, line2 in zip(test_file1, test_file2):
            if line1 != line2:
                logger.error(f"{line1} not equal {line2}")
                return False
        if test_file1.readline() == test_file2.readline():
            result = True
        else:
            result = False
        return result
