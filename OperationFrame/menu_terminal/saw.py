# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2022/08/03
"""
import os
import asyncio
from typing import Union

import uvicorn
import subprocess

from OperationFrame.config import config, platform
from OperationFrame.utils.cbvmenu import CommonCbv, TAG_SAW
from OperationFrame.utils.connecter import cmd_result
from OperationFrame.utils.log import logger

server_name: str = f'{config.ENV}-Server'
worker_name: str = f'{config.ENV}-Worker'


class SaWStatusMixin:
    cmd:           str
    message:       str
    status_print: bool = True

    @classmethod
    async def run(cls) -> str:
        req = await cmd_result(cls.cmd)
        req = str(req).strip()
        pro: str = ''
        mem: float = 0.0
        cpu: float = 0.0
        if not req:
            message = '\nSTATUS: DOWN\n' + cls.message
        else:
            for res in req.split('\n'):
                _res = ' '.join(res.split(' ')).split()
                pro += f'{_res[0]} '
                mem += float(_res[1])
                cpu += float(_res[2])
            message = '\nSTATUS: UP\n' + cls.message + f'\nPROCESS_ID: {pro}\n' + f'MEM %: {mem}%\n' + f'CPU %: {cpu}%'
        if cls.status_print:
            logger.info(message)
        return pro


class SaWStopMixin:
    name:        str
    status_cls: Union['WorkerStatus', 'ServerStatus']

    @classmethod
    async def run(cls):
        cls.status_cls.status_print = False
        pro = await cls.status_cls.run()
        if pro:
            logger.warning(f'即将关闭 {cls.name}, 进程号: {pro}')
            cmd: str = f'skill -9 {pro}'
            req = await cmd_result(cmd)
            if req:
                logger.info(f'{cls.name} 关闭成功')
            else:
                logger.error(f'{cls.name} 关闭失败, {req.stdout} {req.stderr} {req.code}')
                return False
        else:
            logger.warning(f'{cls.name} 已处于关闭状态')
        return True


class SaWRestartMixin:
    stop_cls:   Union['ServerStop', 'WorkerStop']
    start_cls:  Union['ServerStart', 'WorkerStart']
    name:        str
    start_sleep: int = 5

    @classmethod
    async def run(cls):
        if await cls.stop_cls.run():
            logger.warning(f'等待 {cls.start_sleep} 秒将启动 {cls.name}')
            await asyncio.sleep(cls.start_sleep)
            await cls.start_cls.run()


class ServerStart(CommonCbv):
    cmd: list = [
        'gunicorn', 'OperationFrame.ApiFrame.rule:app', '-k uvicorn.workers.UvicornWorker',
        f'-b {config.SERVER_HOST}:{config.SERVER_PORT}',
        f'-w {config.SERVER_WORKER}',
        f'-n {server_name}',
        '--daemon'
    ]

    @classmethod
    def debug_up(cls):
        uvicorn.run(app=cls.cmd[1], host=config.SERVER_HOST,
                    port=config.SERVER_PORT, debug=config.SERVER_DEBUG, reload=config.SERVER_RELOAD)

    @classmethod
    async def run(cls, debug: bool = False):
        if platform == 'win32':
            cls.debug_up()
        else:
            ServerStatus.status_print = False
            if await ServerStatus.run():
                logger.info(f'{server_name} 已处于启动状态')
                return
            if debug is True:
                cls.debug_up()
            else:
                subprocess.run(cls.cmd)
                logger.info(f'{server_name} 启动成功')

    class Meta:
        name = 'server 启动'
        sign = 'server_start'
        tag = TAG_SAW
        depend_mysql = True
        depend_redis = True
        mounted = config.SERVER_MOUNTED


class ServerStatus(SaWStatusMixin, CommonCbv):
    cmd:     str = f'ps -eo pid,%mem,%cpu,cmd |grep {server_name} |grep -v grep'
    message: str = f'SERVER_NAME: {server_name}\nADDRESS: {config.SERVER_HOST}:{config.SERVER_PORT}\n' \
                   f'PROCESS_NUMS: {config.SERVER_WORKER + 1}\nWORKER: {config.SERVER_WORKER}'

    class Meta:
        name = 'server 状态'
        sign = 'server_status'
        tag = TAG_SAW
        depend_mysql = False
        depend_redis = False
        mounted = platform != 'win32' and config.SERVER_MOUNTED


class ServerStop(SaWStopMixin, CommonCbv):
    name:                str = server_name
    status_cls: ServerStatus = ServerStatus

    class Meta:
        name = 'server 关闭'
        sign = 'server_stop'
        tag = TAG_SAW
        mounted = platform != 'win32' and config.SERVER_MOUNTED


class ServerRestart(SaWRestartMixin, CommonCbv):
    stop_cls:   ServerStop = ServerStop
    start_cls: ServerStart = ServerStart
    start_sleep:       int = 3
    name:              str = server_name

    class Meta:
        name = 'server 重启'
        sign = 'server_restart'
        tag = TAG_SAW
        mounted = platform != 'win32' and config.SERVER_MOUNTED


class WorkerStart(CommonCbv):
    cmd: list = ['python3', f'{os.getcwd()}/OperationFrame/ApiFrame/rule_worker.py',  f'-n {worker_name}']

    @classmethod
    async def run(cls, debug: bool = False):
        if platform == 'win32':
            from OperationFrame.ApiFrame.rule_worker import Worker
            await Worker(is_run=False).main()
        else:
            WorkerStatus.status_print = False
            if await WorkerStatus.run():
                logger.info(f'{worker_name} 已处于启动状态')
                return
            if debug is True:
                subprocess.run(cls.cmd)
            else:
                os.system(f"nohup {' '.join(cls.cmd)} &")
                logger.info(f'{worker_name} 启动成功')

    class Meta:
        name = 'worker 启动'
        sign = 'worker_start'
        tag = TAG_SAW
        depend_mysql = True
        depend_redis = True
        mounted = config.SERVER_MOUNTED


class WorkerStatus(SaWStatusMixin, CommonCbv):
    cmd:     str = f'ps -eo pid,%mem,%cpu,cmd |grep {worker_name} |grep -v grep'
    message: str = f'SERVER_NAME: {worker_name}\nPROCESS_NUMS: 1\nMAX_JOBS: {config.WORKER_MAX_JOBS}'

    class Meta:
        name = 'worker 状态'
        sign = 'worker_status'
        tag = TAG_SAW
        depend_mysql = False
        depend_redis = False
        mounted = platform != 'win32' and config.SERVER_MOUNTED


class WorkerStop(SaWStopMixin, CommonCbv):
    name:                str = worker_name
    status_cls: WorkerStatus = WorkerStatus

    class Meta:
        name = 'worker 关闭'
        sign = 'worker_stop'
        tag = TAG_SAW
        depend_mysql = False
        depend_redis = False
        mounted = platform != 'win32' and config.SERVER_MOUNTED


class WorkerRestart(SaWRestartMixin, CommonCbv):
    name:              str = worker_name
    stop_cls:   WorkerStop = WorkerStop
    start_cls: WorkerStart = WorkerStart

    class Meta:
        name = 'worker 重启'
        sign = 'worker_restart'
        tag = TAG_SAW
        mounted = platform != 'win32' and config.SERVER_MOUNTED
