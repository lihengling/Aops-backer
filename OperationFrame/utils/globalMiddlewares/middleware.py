# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2023/03/01
"""
import typing as t
from .triggers import ErrorHandler


class Middleware(ErrorHandler):
    __slots__ = ('_menu_task',)

    _menu_task: t.Callable

    def __init__(self, menu_task: t.Callable):
        self._menu_task = menu_task

    async def __call__(self, *args, **kwargs):
        with self.menu_handler():
            await self._menu_task(*args, **kwargs)
