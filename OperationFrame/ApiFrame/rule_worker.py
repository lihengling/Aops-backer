# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2023/03/30
"""
import os
import sys
from arq.worker import func

sys.path.append(os.getcwd())

from OperationFrame.config import config
from OperationFrame.lib.tools import import_paths
from OperationFrame.utils.log import logger
from OperationFrame.ApiFrame.utils.arq import Worker
from OperationFrame.utils.cbvmenu import TAG_SAW, menu, TYPE_WORKER
from OperationFrame.utils.context import context

# 载入上下文
context.tag = TAG_SAW

# 载入菜单模块
for module in config.TERMINAL_VIEW_DIR:
    import_paths(module)

# 载入 worker 模块
for module, view_dir in config.SERVER_VIEWS_DIR.items():
    import_paths(view_dir)
    logger.debug(f"import models {module}: {config.FRAME_NAME}.{view_dir}")


# 载入菜单 worker
async def _worker_func(ctx, *args, **kwargs):
    return await Worker.tasks_list[ctx['job_name']][0].run(*args, **kwargs)

Worker.tasks_list = {f'{task.sign}': (task.self, task.name) for tasks in menu.tasks.values()
                     for task in tasks if task.route and TYPE_WORKER in task.route.tags}

for name, task in Worker.tasks_list.items():
    Worker.f_jobs.append(func(coroutine=_worker_func, name=name))
    logger.debug(f'register menu task:{name} => {task[1]}')


if __name__ == '__main__':
    Worker()
