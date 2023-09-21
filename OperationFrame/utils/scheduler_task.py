# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2023/06/07
"""
import asyncio
import sys
import time
from asyncio import Task
from typing import Union, Awaitable, Callable

from OperationFrame.config import config
from OperationFrame.lib.scheduler import AsyncScheduler
from OperationFrame.utils.cbvmenu import TAG_SAW
from OperationFrame.utils.context import context
from OperationFrame.utils.log import logger


class SchedulerTasksStatus:
    in_progress: str = 'in_progress'  # 执行中
    complete:    str = 'complete'     # 完成的
    failed:      str = 'failed'       # 失败的
    abort:       str = 'abort'        # 取消的
    retry:       str = 'retry'        # 重试的


class SchedulerTasks(SchedulerTasksStatus):
    __slots__ = ('_sign', '_total', '_failed', '_success', '_cancelled', 'scheduler', 'print_progress', '_loggers'
                 '_log', 'tasks', 'method')

    _sign:          str
    _total:         int
    _failed:        int
    _success:       int
    _cancelled:     int
    _loggers:       list
    _log:           bool
    scheduler:      AsyncScheduler
    print_progress: bool
    tasks:          list
    method:         Union[Awaitable, Callable]

    async def run_task(
            self,
            mcs_method: Union[Awaitable, Callable] = None,
            task_list: list = None,
            *args, **kwargs
    ) -> str:
        if not getattr(self, 'scheduler', None) and task_list:
            self.make_scheduler(mcs_method)
            self.add_task(mcs_method, task_list, *args, **kwargs)

        self._total = len(self.scheduler)
        if self._total <= 0:
            logger.warning(f"{self.method.__name__} 任务提供参数为空, 请检查")
            return self.failed

        self.__tasks_progress()
        try:
            await self.scheduler.join()
        except asyncio.CancelledError:
            for task in self.tasks:
                if not task.done():
                    task.cancel()

        await asyncio.sleep(1)
        if self._failed != 0:
            return self.failed
        elif self._cancelled != 0:
            return self.abort
        elif (self._cancelled + self._failed) == 0 and self._success >= 0:
            return self.complete
        else:
            return self.in_progress

    def add_task(
            self,
            mcs_method: Union[Awaitable, Callable],
            task_list: list,
            *args, **kwargs
    ) -> None:
        method_name:          str = mcs_method.__name__
        method_date:          str = time.strftime('%Y%m%d', time.localtime(time.time()))
        format_kwargs = ', '.join(f"{key}='{value}'" for key, value in kwargs.items())

        for task in task_list:
            if not isinstance(task, tuple):
                task = (task, )
            job = task[0]
            if isinstance(job, list):
                job = '_'.join(job)

            coroutine_name = f"{method_name} ('{str(*task)}'"
            if args:
                args_str = ', '.join([(f"'{x}'" if not isinstance(x, (tuple, list, dict)) else f'{x}') for x in args])
                coroutine_name += f", {args_str}"
            if format_kwargs:
                coroutine_name += f", {format_kwargs}"
            coroutine_name += ")"

            if self._log:
                logger_id = logger.add_task_file(f'{config.LOGS_MULTI_DIR}/{method_name}_{job}_{method_date}.log')
                self._loggers.append(logger_id)
            with logger.contextualize(context=f"{method_name}_{job}"):
                logger.info(f'\033[32m##### {coroutine_name} Task Begin  #####\033[0m')
                coroutine_task: Task = self.scheduler.create_task(mcs_method(*task, *args, **kwargs))
                coroutine_task.set_name(coroutine_name)
                self.tasks.append(coroutine_task)

    @staticmethod
    def get_max_worker(method_name) -> int:
        for worker in config.TASK_MAX_WORKER:
            if len(worker) >= 2 and method_name in worker[1:] and worker[0].isdigit():
                return int(worker[0])
        return config.TASK_DEFAULT_WORKER

    def make_scheduler(self, mcs_method: Union[Awaitable, Callable], log=True) -> AsyncScheduler:
        self._failed:         int = 0
        self._success:        int = 0
        self._cancelled:      int = 0
        self._loggers:       list = []
        self._log:           bool = log
        self.print_progress: bool = context.tag != TAG_SAW and log
        self.scheduler = AsyncScheduler(stack_limit=False, task_done=self.__task_done if log else None,
                                        max_workers=self.get_max_worker(mcs_method.__name__))
        self.method = mcs_method
        self.tasks:          list = []
        return self.scheduler

    def __task_done(self, task: Task):
        task_res:       Union[BaseException, None, bool]
        task_exception: Union[BaseException, None]
        task_name:      str = task.get_name()
        task_stack:    list = task.get_stack()
        try:
            task_res = task.result()
        except BaseException as err:
            task_res = err
        try:
            task_exception = task.exception()
        except BaseException as err:
            task_exception = err

        if task.cancelled() is True:
            self._cancelled += 1
            logger.warning(f'Task Cancelled => {type(task_exception)}')
            logger.warning(f'{task_name} 终止', task=task_name)

        elif task_stack or task_res is False or isinstance(task_res, BaseException) \
                or (task_res is not None and bool(task_res) is False):
            self._failed += 1
            if task_exception:
                logger.error(f'{task_exception}')
            if task_stack:
                logger.error('\n'.join([str(x) for x in task_stack]))
            logger.error(f'{task_name} 失败', task=task_name)
        else:
            self._success += 1
            logger.info(f'{task_name} 成功', task=task_name)

        logger.info(f'\033[32m##### {task_name} Task Finish #####\033[0m')
        self.__tasks_progress()

    def __tasks_progress(self):
        pro: int = self._success + self._failed + self._cancelled
        pro_message: str = f"[ {(pro / self._total * 100):.0f}% ] Total: {self._total} Success: {self._success} " \
                           f"Failed: {self._failed}"

        if context.tag != TAG_SAW and self.print_progress:
            if pro == self._total and self._failed == 0 and self._cancelled == 0:
                logger.info(f'Finish | {pro_message} Cancelled: {self._cancelled}', task='Finish')
            elif pro == self._total:
                logger.warning(f'Finish | {pro_message} Cancelled: {self._cancelled}', task='Finish')
            elif self._cancelled == 0:
                sys.stdout.write(f"InProgress | {pro_message} \r")

        if pro == self._total and pro > 0:
            for _logger in self._loggers:
                logger.remove(_logger)
