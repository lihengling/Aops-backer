# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2023/03/01
"""


class MenuBaseError(Exception):
    error:   str
    message: any

    def __init__(self, message: any = None):
        if message:
            self.message = message
        if not hasattr(self, 'message'):
            self.message = self.error

    def __str__(self):
        return self.error


class MenuLostError(MenuBaseError):
    error:     str = '未被定义的菜单模块'
    message:   str = '传入菜单模块不存在'


class MenuParamError(MenuBaseError):
    error:     str = '参数错误的菜单模块'


class MenuMountedError(MenuBaseError):
    error:     str = '未被挂载的菜单模块'
    message:   str = '菜单未被挂载使用, 请检查菜单 mounted 参数'


class MenuDependError(MenuBaseError):
    error:     str = '依赖项错误菜单模块'
