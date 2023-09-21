# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2023/03/30
"""
import os


def is_file_changed(file_path: str) -> bool:
    current_stat = os.stat(file_path)
    if current_stat.st_mtime != is_file_changed.previous_stat.st_mtime:
        is_file_changed.previous_stat = current_stat
        return True
    return False
