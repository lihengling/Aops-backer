# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2022/07/21
"""
import os
import re
import hashlib
import aiofiles

from typing import Union
from importlib import import_module

from OperationFrame.config import config, platform
from OperationFrame.lib.depend import PageQuery


def import_paths(module: str):
    """
    module 模块 name
    递归导入 module 下的资源
    """
    platform_dir = f'{config.PROJECT_PATH}.{module}'
    platform_dir = platform_dir.replace('.', '/') if platform != 'win32' else platform_dir.replace('.', '\\')

    for path, _, files in os.walk(platform_dir):
        for file in files:
            _path = path.split(str(config.PROJECT_PATH))[1].replace('/', '.').replace('\\', '.')
            _path = f"{config.FRAME_NAME}{_path}"
            if not _path.split('.')[-1].startswith('_') or path.split('.')[-1] == '__init__':
                import_module(f"{_path}.{file.split('.')[0]}")


def md5_value(value: str, time: str) -> str:
    """
    对 value/time 进行 md5 加密
        value: 需加密字符串
        time: 加密时间
    """
    rud_key_md5 = hashlib.md5()
    rud_key_md5.update(f"{time}{value}".encode())
    rud_key_md5_pwd = rud_key_md5.hexdigest()
    return rud_key_md5_pwd


def md5_sha256_value(value: str, time: str) -> str:
    """
    对 value/time 进行 md5、sha256 加密
        value: 需加密字符串
        time: 加密时间
    """
    rud_key_md5_pwd = md5_value(value, time)
    rud_key_sha256 = hashlib.sha256()
    rud_key_sha256.update(rud_key_md5_pwd.encode())
    encrypt_value = rud_key_sha256.hexdigest()
    return encrypt_value


def paginate_list(data_list: list, page_query: Union[PageQuery, dict]):
    """
    列表分页器
    """
    if isinstance(page_query, dict):
        page_query = PageQuery(**page_query)

    total_pages = (len(data_list) + page_query.pageSize - 1) // page_query.pageSize
    paginated_list = []

    start_index = (page_query.pageIndex - 1) * page_query.pageSize
    end_index = start_index + page_query.pageSize

    if start_index >= len(data_list):
        return [], total_pages

    if end_index > len(data_list):
        end_index = len(data_list)

    while start_index < end_index:
        paginated_list.append(data_list[start_index])
        start_index += 1

    return paginated_list, total_pages


def is_ip_address(ip_address: str) -> bool:
    """
    匹配ip地址
    """
    return bool(re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', ip_address))


class Print:
    class Color:
        ERROR:   str = '\033[91m'
        INFO:    str = '\033[32m'
        DEBUG:   str = '\033[34m'
        WARNING: str = '\033[33m'
        RESET:   str = '\033[0m'

    @classmethod
    def info(cls, msg):
        print(f'{cls.Color.INFO}{msg}{cls.Color.RESET}')

    @classmethod
    def warning(cls, msg):
        print(f'{cls.Color.WARNING}{msg}{cls.Color.RESET}')

    @classmethod
    def error(cls, msg):
        print(f'{cls.Color.ERROR}{msg}{cls.Color.RESET}')

    @classmethod
    def debug(cls, msg):
        print(f'{cls.Color.DEBUG}{msg}{cls.Color.RESET}')


async def get_file(file: str) -> list:
    """
    以列表方式返回文件内容
    """
    line = []
    try:
        async with aiofiles.open(file, 'r') as f:
            line = await f.readlines()
            line = [line.strip() for line in line]
    except FileNotFoundError:
        pass

    return line
