# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2023/03/30
"""
import time
import types

import redis
from redis import Redis
from tortoise import Tortoise
from datetime import datetime, timedelta
from typing import TypedDict, Union, List, Optional

from OperationFrame.utils.globalMiddlewares.event import real_time
from .run_job import Worker as BaseWorker
from arq import ArqRedis
from arq.connections import RedisSettings, create_pool
from arq.cron import CronJob, cron
from arq.typing import OptionType, WeekdayOptionType, SecondsTimedelta
from arq.worker import Function

from OperationFrame.config import config
from OperationFrame.utils.context import context
from OperationFrame.utils.log import logger


class BaseCTX(TypedDict):
    redis: ArqRedis


class CTX(BaseCTX):
    job_name: str
    job_logger_id: int
    job_id: str
    job_try: int
    job_start_time: timedelta
    job_end_time: timedelta
    score: int
    enqueue_time: datetime


class Worker(BaseWorker):
    f_jobs: List[Union[Function, types.CoroutineType]] = []
    c_jobs: List[CronJob] = []

    def __init__(self, is_run: bool = True, **kwargs):
        self.__dict__.update(kwargs)
        if self.f_jobs or self.c_jobs:
            super().__init__(
                functions=self.f_jobs or [],
                cron_jobs=self.c_jobs or [],
                on_startup=self.startup,
                on_shutdown=self.shutdown,
                on_job_start=self.on_job_start,
                max_jobs=config.WORKER_MAX_JOBS,
                on_job_end=self.on_job_end,
                allow_abort_jobs=True,
                redis_settings=RedisSettings().from_dsn(config.WORKER_DSN),
                keep_result=config.WORKER_KEEP
            )
            if is_run:
                self.run()

    @classmethod
    async def create_pool(cls) -> ArqRedis:
        return await create_pool(RedisSettings().from_dsn(config.WORKER_DSN))

    async def startup(self, ctx: BaseCTX):
        await Tortoise.init(
            db_url=config.MYSQL_ENGINE,
            modules={'models': config.MYSQL_REGISTER_MODEL}
        )
        logger.debug(f'Worker init tortoise: {Tortoise._inited}')

        context.redis = Redis.from_url(config.WORKER_DSN)
        context.pool = await Worker.create_pool()
        try:
            context.redis_connected = context.redis.ping()
        except redis.exceptions.AuthenticationError:
            pass
        logger.debug(f"task len: {len(self.f_jobs)} cron len: {len(self.c_jobs)}")
        logger.debug(f'Worker init redis: {context.redis_connected}')
        logger.debug(f"Worker Startup {'complete' if context.redis_connected and Tortoise._inited else 'failed'}")

    @staticmethod
    async def shutdown(ctx: CTX):
        pass

    @staticmethod
    async def on_job_start(ctx: CTX):
        if 'cron' not in ctx['job_name']:
            milliseconds = int(round(time.time() * 1000))
            ctx['job_logger_id'] = logger.add_worker_file(
                f"{config.LOGS_WORKER_DIR}/{milliseconds}%{ctx['job_id']}%{ctx['job_name']}" +
                "-{time:YYYY-MM-DD-HH#mm#ss}.log", ctx['job_id']
            )
            ctx['job_start_time'] = real_time()

    @staticmethod
    async def on_job_end(ctx: CTX):
        if 'cron' not in ctx['job_name']:
            ctx['job_end_time'] = real_time()
            logger.info(f"RunTime: {ctx['job_end_time'] - ctx['job_start_time']}")
            logger.remove(ctx['job_logger_id'])

    @classmethod
    def task(cls, summary: str = ''):
        """
        await context.pool.enqueue_job('ping_task', 'message')
        """
        def wrapper(func):
            logger.debug(f'register task:{func.__name__} => {summary}')
            cls.f_jobs.append(func)

        return wrapper

    @classmethod
    def cron(cls,
             name: Optional[str] = None,
             month: OptionType = None,
             day: OptionType = None,
             weekday: WeekdayOptionType = None,
             hour: OptionType = None,
             minute: OptionType = None,
             second: OptionType = 0,
             microsecond: int = 123_456,
             run_at_startup: bool = False,
             unique: bool = True,
             timeout: Optional[SecondsTimedelta] = None,
             keep_result: Optional[float] = 0,
             keep_result_forever: Optional[bool] = False,
             max_tries: Optional[int] = 1,
             summary: str = ''):

        def wrapper(func):
            logger.debug(f'register cron:{func.__name__} => {summary}')
            cls.c_jobs.append(
                cron(func, name=name, month=month, day=day, weekday=weekday, hour=hour, minute=minute,
                     second=second, microsecond=microsecond, run_at_startup=run_at_startup, unique=unique,
                     timeout=timeout, keep_result=keep_result, keep_result_forever=keep_result_forever,
                     max_tries=max_tries)
            )

        return wrapper
