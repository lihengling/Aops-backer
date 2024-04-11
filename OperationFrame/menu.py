# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2022/07/19
"""
import asyncio
import typing as t

from OperationFrame.config import config
from OperationFrame.lib.tools import import_paths
from OperationFrame.utils.cbvmenu import menu
from OperationFrame.utils.context import context
from OperationFrame.utils.globalMiddlewares import Middleware, MenuLostError, MenuParamError, \
    MenuMountedError, MenuDependError
from OperationFrame.utils.log import logger


# 载入菜单模块
for module in config.TERMINAL_VIEW_DIR:
    import_paths(module)


@Middleware
@logger.catch(exclude=(MenuLostError, MenuParamError, MenuMountedError, MenuDependError))
async def menu_enter(argv: t.List):
    # 处理参数
    argv, task_kwargs, task = handle_params(argv)

    # 依赖写入上下文
    context.tag = task.tag
    context.depend_mysql = task.depend_mysql
    context.depend_redis = task.depend_redis

    async with menu.lifespan_context():
        if asyncio.iscoroutinefunction(task.self.run):
            await task.self.run_with_logger(*argv[2:], **task_kwargs)
        else:
            task.self.run_with_logger(*argv[2:], **task_kwargs)


def handle_params(argv: t.List) -> tuple:
    param_num = len(argv)
    if param_num <= 1:
        raise MenuLostError
    task = menu[argv[1]]
    if not task:
        raise MenuLostError

    if not task.mounted:
        raise MenuMountedError

    task_kwargs: dict = {}
    input_args:  list = argv[2:]
    task_args:   list = task.params.split(', ')
    _task_args:  list = [x for x in task_args if not x.startswith('--')]
    task_args.remove('None') if 'None' in task_args else None

    for arg in input_args:
        if '--' in arg:
            argv.remove(arg)
            try:
                key, value = arg.strip('-').split('=')
            except ValueError:
                raise MenuParamError(message=f'{arg} 传递参数有误, 期望值: {arg}=x | 传递值: {arg}')
            if not value:
                raise MenuParamError(message=f'{arg} 传递参数有误, 期望值: {arg}=x | 传递值: {arg}')
            if key and f'--{key}' in task_args and value:
                try:
                    e_value = eval(value)
                    task_kwargs[key] = str(e_value) if not bool(e_value) else e_value
                except (NameError, SyntaxError):
                    task_kwargs[key] = str(value)
            else:
                raise MenuParamError(message=f'{arg} 传递参数有误, 期望值: {task_args} | 传递值: {arg}')

    if 'None' in _task_args:
        _task_args.remove('None')

    if len(input_args) > len(_task_args) + len(task_kwargs):
        raise MenuParamError(message=f'接收参数:{task_args}, 提供参数:{input_args}')

    argv.extend([None] * (len(_task_args) - len(input_args) + len(task_kwargs)))

    return argv, task_kwargs, task
