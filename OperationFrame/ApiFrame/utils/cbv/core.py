# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2023/04/07
"""
from functools import reduce
from operator import or_
from typing import cast, Type, List, Union

from fastapi import APIRouter, Security
from tortoise.expressions import Q
from tortoise.models import Model
from tortoise.contrib.pydantic import pydantic_model_creator
from fastapi_crudrouter import TortoiseCRUDRouter

from OperationFrame.ApiFrame.base import ROUTER_START_SWITCH, PERMISSION_INFO, PERMISSION_DELETE, PERMISSION_UPDATE, \
    NotFindError
from OperationFrame.ApiFrame.utils.jwt import check_permissions
from OperationFrame.lib.depend import paginate_factory
from OperationFrame.utils.models import BaseResponse


# 数据库模型：模糊匹配字段           (以列表形式定义在 Meta 中)
QUERY_FIELDS:                    str = 'query_fields'
# 数据库模型：注册路由接口所有允许字段 (以列表形式定义在 Meta 中)
ALLOW_REGISTRY_ROUTE:           list = [
    'get_all', 'get_one',       # get    方法: 获取所有资源、获取单个资源
    'create_one',               # post   方法: 创建单个资源
    'update_one',               # put    方法: 修改单个资源
    'delete_all', 'delete_one'  # delete 方法: 删除所有资源、删除单个资源
]


def get_cbv_exp(model: Type[Model], query) -> list:
    if hasattr(model.Meta, QUERY_FIELDS):
        query_fields: Union[set, list] = getattr(model.Meta, QUERY_FIELDS)
        query_fields = set(query_fields).intersection(model._meta.fields)
    else:
        query_fields = model._meta.fields

    return [Q(**{f"{x}__icontains": query}) for x in query_fields
            if not x.startswith('_') and x not in model._meta.fetch_fields]


def get_cbv_router(tortoise_model: Type[Model], sort: str = None, make_rpcEndpoint: bool = True) -> APIRouter:
    # 生成基础路由属性
    model_name = tortoise_model.__name__.lower()
    schema = pydantic_model_creator(tortoise_model, name=f"{tortoise_model.__name__}Schema")
    router = TortoiseCRUDRouter(
        schema=schema,
        db_model=tortoise_model,
        prefix=f"{ROUTER_START_SWITCH}/{model_name}",
        tags=[tortoise_model.__name__],
        get_all_route=False, get_one_route=False, create_route=False,
        update_route=False, delete_one_route=False, delete_all_route=False
    )
    route_registry = getattr(tortoise_model.Meta, 'route_registry', ALLOW_REGISTRY_ROUTE)

    if 'get_all' in route_registry:
        @router.get('', summary=f"CBV 获取 {model_name} 模型列表", response_model=BaseResponse[List[schema]],
                    dependencies=[Security(check_permissions, scopes=[f'{model_name}_{PERMISSION_INFO}'])])
        async def overloaded_get_all(pagination: dict = paginate_factory(), query: Union[str, int] = None):
            skip, limit = pagination.get("skip", 0), pagination.get("limit", None)
            if query is not None:
                _query_model = router.db_model.filter(reduce(or_, get_cbv_exp(router.db_model, query)))
            else:
                _query_model = router.db_model
            req = _query_model.all().offset(cast(int, skip))
            if limit:
                req = req.limit(limit)
            _req = await req
            return BaseResponse(data=_req)

    if 'delete_all' in route_registry:
        @router.delete('', summary=f"CBV 删除 {model_name} 模型列表", response_model=BaseResponse[List[schema]],
                    dependencies=[Security(check_permissions, scopes=[f'{model_name}_{PERMISSION_DELETE}'])])
        async def overloaded_delete_all():
            req = await router._get_all()(pagination={"skip": 0, "limit": None})
            await router.db_model.all().delete()
            return BaseResponse(data=req)

    if 'create_one' in route_registry:
        @router.post('', summary=f"CBV 创建 {model_name} 模型资源", response_model=BaseResponse[schema],
                    dependencies=[Security(check_permissions, scopes=[f'{model_name}_{PERMISSION_UPDATE}'])])
        async def overloaded_create(model: Union[router.create_schema, dict]):
            if isinstance(model, dict):
                req = router.db_model(**model)
            else:
                req = router.db_model(**model.dict())
            await req.save()
            return BaseResponse(data=req)

    if 'get_one' in route_registry:
        @router.get('/{item_id}', summary=f"CBV 获取 {model_name} 模型单个资源", response_model=BaseResponse[schema],
                    dependencies=[Security(check_permissions, scopes=[f'{model_name}_{PERMISSION_INFO}'])])
        async def overloaded_get_one(item_id: int):
            req = await router.db_model.filter(id=item_id).first()
            if req:
                return BaseResponse(data=req)
            else:
                raise NotFindError

    if 'update_one' in route_registry:
        @router.put('/{item_id}', summary=f"CBV 更新 {model_name} 模型单个资源", response_model=BaseResponse[schema],
                    dependencies=[Security(check_permissions, scopes=[f'{model_name}_{PERMISSION_UPDATE}'])])
        async def overloaded_update(item_id: int, model: Union[router.create_schema, dict]):
            if not isinstance(model, dict):
                model = model.dict(exclude_unset=True)
            if not await router.db_model.filter(id=item_id).update(**model):
                raise NotFindError
            req: Model = await router._get_one()(item_id)
            return BaseResponse(data=req)

    if 'delete_one' in route_registry:
        @router.delete('/{item_id}', summary=f"CBV 删除 {model_name} 模型单个资源", response_model=BaseResponse[schema],
                    dependencies=[Security(check_permissions, scopes=[f'{model_name}_{PERMISSION_DELETE}'])])
        async def overloaded_delete_one(item_id: int):
            req = await router.db_model.filter(id=item_id).first()
            if not req:
                raise NotFindError
            await router.db_model.filter(id=item_id).delete()
            return BaseResponse(data=req)

    if sort:
        router.sort = sort
    if make_rpcEndpoint:
        for route in router.routes:
            route.rpc_endpoint = f"{model_name}_{route.endpoint.__name__[11:]}"

    return router
