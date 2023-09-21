# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2023/03/01
"""
import contextlib
from asyncio.exceptions import CancelledError

from .event import menu
from .error_classify import MenuBaseError
from ..cbvmenu import TAG_U_MOUNTED


class ErrorHandler:
    help_header: str = "usage: ./main.py Action [options]\n"

    def _menu_help(self):
        print(self.help_header)
        _menu = {k: v for k, v in sorted(menu.tasks.items(), key=lambda x: x[0] != TAG_U_MOUNTED)}
        for tag, task in _menu.items():
            message = f"{tag} {[len(task)]}\n"
            for task_obj in task:
                format_param = str([task_obj.params]).replace("'", "")
                message += f"    {task_obj.sign:<25}" \
                           f"{('<Log: Open>' if task_obj.log else '<Log: Closed>'):<20}{task_obj.name}     " \
                           f"{format_param}\n"
            print(message)

    @contextlib.contextmanager
    def menu_handler(self):
        try:
            yield
        except BaseException as err:
            if isinstance(err, MenuBaseError):
                self._menu_help()
                error = err.__str__()
                message = err.message or error
            elif isinstance(err, KeyboardInterrupt):
                error = message = f'取消执行菜单'
            elif isinstance(err, CancelledError):
                error = message = f'任务终止的菜单'
            elif isinstance(err, SystemExit):
                error = message = f'进程主动退出'
            else:
                error = message = '未定义的错误'

            print(f"{error} | 错误类型: {type(err)} | 错误信息: {message}")
