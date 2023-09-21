# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2023/03/01
"""
import time
import datetime

from redis import Redis
from tortoise import Tortoise
from redis.exceptions import AuthenticationError, ConnectionError
from tortoise.exceptions import DBConnectionError, OperationalError, ConfigurationError

from OperationFrame.config import config
from OperationFrame.utils.aerich import aer
from OperationFrame.utils.cbvmenu import menu
from OperationFrame.utils.context import context
from OperationFrame.utils.globalMiddlewares.error_classify import MenuDependError
from OperationFrame.utils.log import logger


def real_time() -> datetime.timedelta:
    return datetime.timedelta(seconds=int(str(time.time()).split(".")[0]))


startup = real_time()


@menu.on_event("startup")
async def init_tortoise():
    async def _init(_create_db: bool = False):
        await Tortoise.init(
            db_url=config.MYSQL_ENGINE,
            modules={'models': config.MYSQL_MENU_MODEL},
            _create_db=_create_db
        )
    try:
        if context.depend_mysql:
            await _init(_create_db=True)
    except (DBConnectionError, OperationalError, ConfigurationError) as e:
        if isinstance(e, (DBConnectionError, ConfigurationError)):
            raise MenuDependError(message=f'Mysql {e} - {type(e)}')
        await _init()


@menu.on_event("startup")
async def init_redis():
    try:
        if context.depend_redis:
            context.redis = Redis.from_url(config.WORKER_DSN)
            context.redis_connected = context.redis.ping()
    except (AuthenticationError, ConnectionError, ValueError) as e:
        raise MenuDependError(message=f'Redis {e} - {type(e)}')


@menu.on_event("startup")
async def init_aer():
    try:
        if context.depend_mysql:
            await aer.init()
    except DBConnectionError as e:
        raise MenuDependError(message=f'aer Mysql {e} - {type(e)}')


@menu.on_event("shutdown")
async def close_tortoise():
    if Tortoise._inited:
        await Tortoise.close_connections()


@menu.on_event("shutdown")
async def run_time():
    logger.info(f"RunTime: {real_time() - startup}")
    if context.log_id is not None and isinstance(context.log_id, int):
        logger.remove(context.log_id)
