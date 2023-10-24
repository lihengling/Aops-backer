# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2022/07/21
"""
import os
import glob
import time
from asyncio.exceptions import CancelledError
from typing import Callable, Awaitable, Union, List, Coroutine

from OperationFrame.config import config
from OperationFrame.utils.cbvmenu import MenuMetaClass, BaseMeta, TAG_SAW
from OperationFrame.utils.connecter import CmdResultHandle
from OperationFrame.utils.context import context
from OperationFrame.utils.log import logger
from OperationFrame.utils.models import BaseResponse, JobResponse
from OperationFrame.utils.scheduler_task import SchedulerTasks
from OperationFrame.utils.user_interactive import ask_yesno, ask_input


class __CbvMixin(SchedulerTasks):
    Meta:       BaseMeta = BaseMeta

    @property
    def __run(self) -> Union[Callable, Awaitable, None]:
        return getattr(self, 'run', None)

    async def run_with_logger(self, *args, **kwargs):
        _log: bool = getattr(self.Meta, 'log', False)
        if self.__run is None or not callable(self.__run):
            logger.warning(f'{self} 不存在启动入口或启动入口不可调用')
            return False

        if _log is True:
            milliseconds = int(round(time.time() * 1000))
            logger_id = logger.add_worker_file(f"{config.LOGS_WORKER_DIR}/{milliseconds}%{self.Meta.sign}"
                                               + "-{time:YYYY-MM-DD-HH#mm#ss}.log")
            try:
                context.log_id = logger_id
                req = await self.__run(*args, **kwargs)
            except BaseException as err:
                if not isinstance(err, CancelledError):
                    matched_files = glob.glob(os.path.join(config.LOGS_WORKER_DIR, f"{milliseconds}*"))
                    os.remove(matched_files[0])
                raise err
        else:
            req = await self.__run(*args, **kwargs)
        return req

    async def run_with_worker(self, *args, **kwargs):
        if context.tag == TAG_SAW and context.pool is not None:
            job = await context.pool.enqueue_job(f'{self.Meta.sign}', *args, **kwargs)
            return BaseResponse[JobResponse](data=JobResponse(job_id=job.job_id))
        else:
            return await self.__run(*args, **kwargs)

    def run_confirm(self, objs: Union[List[any], str], *args, **kwargs):
        if context.tag != TAG_SAW:
            logger.info(f'objs: {objs}')
            if args or kwargs:
                args_str = ', '.join([(f"'{x}'" if not isinstance(x, (tuple, list, dict)) else f'{x}') for x in args])
                kwargs_str = ', '.join(f'{key}={value}' for key, value in kwargs.items())
                logger.info(f'params: {args_str} | {kwargs_str}')
            if not ask_yesno('请确认上述参数无误进行任务'):
                return self.failed
        else:
            return True

    async def run_operator(self, objs: Union[List[any], str], *args, **kwargs) -> str:
        """
        objs: 执行任务对象
        args/kwargs: 辅助执行任务参数
        若定义 args/kwargs, 此控制器会对 objs 的每个对象都执行以 args/kwargs 为参数的任务
        """
        if isinstance(objs, str):
            objs = [objs]

        if self.run_confirm(objs, *args, **kwargs) is self.failed:
            return self.failed

        if getattr(self.Meta, 'func', None) is None:
            logger.error('若使用 run_operator 运行任务, 请在 Meta 定义 func 运行任务')
            return self.failed

        methods = self.Meta.func if isinstance(self.Meta.func, list) else [self.Meta.func]
        for method in methods:
            if isinstance(method, Coroutine):
                await method
                continue

            if len(objs) == 1:
                res = await method(objs[0], *args, **kwargs)
                if res is False or (isinstance(res, CmdResultHandle) and not res):
                    return self.failed
            else:
                req = await self.run_task(method, objs, *args, **kwargs)
                if req != self.complete:
                    return req
        return self.complete


class CommonCbv(__CbvMixin, metaclass=MenuMetaClass):
    async def run(self, *args, **kwargs):
        pass


class GameCbv(__CbvMixin, metaclass=MenuMetaClass):
    async def run(self, srv_id: str) -> str:
        cb: str = ','
        srv_id: Union[list, str] = srv_id or (ask_input('输入对象', checkbox=cb, req='list') if context.tag != TAG_SAW else None)
        srv_list = srv_id.split(cb) if isinstance(srv_id, str) else srv_id
        return await self.run_operator(srv_list)

    async def run_with_worker(self, srv_id: str):
        return await super().run_with_worker(srv_id)
