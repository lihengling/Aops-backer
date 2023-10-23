# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2022/08/03
"""
import json
import redis
from redis import Redis
from tortoise import Tortoise
from fastapi import HTTPException as FHTTPException
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as SHTTPException

from OperationFrame.ApiFrame.apps import CBV_MODELS
from OperationFrame.ApiFrame.utils.arq import Worker
from OperationFrame.ApiFrame.utils.cbv import get_cbv_router
from OperationFrame.config import config
from OperationFrame.config.constant import CACHES_CONFIG_KEY, SERVER_TAG_HTTP, SERVER_TAG_RPC
from OperationFrame.utils.cbvmenu import TAG_SAW, menu, TYPE_WORKER
from OperationFrame.utils.context import context
from OperationFrame.utils.log import logger
from OperationFrame.ApiFrame.utils.rpc import rpc
from OperationFrame.ApiFrame.utils.rpc.constant import RPC_DOCS_URL
from OperationFrame.lib.tools import import_paths
from OperationFrame.ApiFrame.base import app, Middleware, Routers, exception_handler, ROUTER_SORT_APP, router_index

# 载入logger/上下文
context.tag = TAG_SAW
logger.add_request()

# 载入菜单模块
for module in config.TERMINAL_VIEW_DIR:
    import_paths(module)

# 载入模块
for module, view_dir in config.SERVER_VIEWS_DIR.items():
    import_paths(view_dir)
    logger.debug(f"import models {module}: {config.FRAME_NAME}.{view_dir}")

# 载入菜单接口
for _type, _tasks in menu.tasks.items():
    for task in _tasks:
        if task.mounted and task.route:
            task.route.path = f"{router_index.prefix}{task.route.path}"
            endpoint = task.self.run_with_worker if TYPE_WORKER in task.route.tags else task.self.run
            menu_route = router_index.route_class(**task.route.dict(),  endpoint=endpoint)
            menu_route.rpc_endpoint = task.sign
            router_index.routes.append(menu_route)
            logger.debug(f"add menu route: {task.route.path}")

# 载入菜单任务
Worker.tasks_list = {f'Worker_{task.sign}': (task.self, task.name) for tasks in menu.tasks.values()
                     for task in tasks if task.route and TYPE_WORKER in task.route.tags}

# 载入路由
if config.SERVER_TYPE == SERVER_TAG_HTTP:
    for route in Routers:
        if not config.VERIFY_TYPE_AUTH and route.sort == ROUTER_SORT_APP:
            continue
        app.include_router(route)
        logger.debug(f"include router: {route.sort} => {route.prefix}")

# 载入 cbv 路由
for sort, models in CBV_MODELS.items():
    for model in models:
        if not config.VERIFY_TYPE_AUTH and sort == ROUTER_SORT_APP:
            continue
        router = get_cbv_router(model, sort)
        Routers.append(router)
        if config.SERVER_TYPE != SERVER_TAG_HTTP:
            continue
        app.include_router(router)
        logger.debug(f"include cbv: {sort} => {router.prefix}")

# 载入中间件
for name, middleware in Middleware[::-1]:
    app.add_middleware(middleware)
    logger.debug(f"add middleware: {name}")

# 载入错误处理器
EXCEPTION_LOG_HANDLER = (Exception, FHTTPException, SHTTPException, RequestValidationError)
for e in EXCEPTION_LOG_HANDLER:
    app.add_exception_handler(e, exception_handler)
    logger.debug(f"add exception handler {e.__module__}.{e.__name__}")

# 载入 rpc
if config.SERVER_TYPE == SERVER_TAG_RPC:
    for router in Routers:
        if not config.VERIFY_TYPE_AUTH and router.sort == ROUTER_SORT_APP: continue
        for route in router.routes:
            endpoint = route.rpc_endpoint if hasattr(route, 'rpc_endpoint') else None
            rpc.register_function(route.endpoint, endpoint)
            logger.debug(f"include rpc: {endpoint or route.endpoint.__name__}")

# 接口文档
if config.SERVER_DEBUG:
    server = f"http://{config.SERVER_HOST}:{config.SERVER_PORT}"
    if config.SERVER_TYPE == SERVER_TAG_RPC:
        logger.debug(f"rpc docs: {server}{RPC_DOCS_URL}")
    else:
        logger.debug(f"api docs: {server}{app.docs_url} / {server}{app.redoc_url}")


# 载入启动事件
@app.on_event("startup")
async def init_tortoise():
    await Tortoise.init(
        db_url=config.MYSQL_ENGINE,
        modules={'models': config.MYSQL_REGISTER_MODEL}
    )
    logger.debug(f'{TAG_SAW} init tortoise: {Tortoise._inited}')
    logger.debug(f"Server type: {config.SERVER_TYPE}")


@app.on_event("startup")
async def init_redis():
    context.redis = Redis.from_url(config.WORKER_DSN)
    try:
        context.redis_connected = context.redis.ping()
    except redis.exceptions.AuthenticationError:
        pass

    if context.redis_connected:
        context.redis.set(CACHES_CONFIG_KEY, json.dumps(config.config_property))
    context.pool = await Worker.create_pool()
    logger.debug(f'{TAG_SAW} init worker pool: {await context.pool.ping()}')
    logger.debug(f'{TAG_SAW} init redis: {context.redis_connected}')


@app.on_event("shutdown")
async def close_redis():
    if context.redis_connected:
        context.redis.quit()
