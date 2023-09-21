# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2023/04/07
"""
from functools import reduce
from operator import or_
from typing import cast, Type, List, Union

from fastapi import APIRouter
from tortoise.expressions import Q
from tortoise.models import Model
from tortoise.contrib.pydantic import pydantic_model_creator
from fastapi_crudrouter import TortoiseCRUDRouter
from fastapi_crudrouter.core._utils import pagination_factory

from OperationFrame.ApiFrame.base import ROUTER_START_SWITCH, NotFindError
from OperationFrame.utils.models import BaseResponse

_pagination_factory = pagination_factory()


def get_cbv_exp(model: Type[Model], query) -> list:
    if hasattr(model.Meta, 'query_fields'):
        query_fields: Union[set, list] = getattr(model.Meta, 'query_fields')
        query_fields = set(query_fields).intersection(model._meta.fields)
    else:
        query_fields = model._meta.fields
    return [Q(**{f"{x}__icontains": query}) for x in query_fields if not x.startswith('_')]


def get_cbv_router(tortoise_model: Type[Model], sort: str = None, make_rpcEndpoint: bool = True) -> APIRouter:
    model_name = tortoise_model.__name__.lower()
    schema = pydantic_model_creator(tortoise_model, name=f"{tortoise_model.__name__}Schema")
    router = TortoiseCRUDRouter(
        schema=schema,
        db_model=tortoise_model,
        prefix=f"{ROUTER_START_SWITCH}/{model_name}",
        tags=[tortoise_model.__name__],
    )

    @router.get('', summary=f"获取 {model_name} 模型列表", response_model=BaseResponse[List[schema]])
    async def overloaded_get_all(pagination: dict = _pagination_factory, query: Union[str, int] = None):
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

    @router.delete('', summary=f"删除 {model_name} 模型列表", response_model=BaseResponse[List[schema]])
    async def overloaded_delete_all():
        req = await router._get_all()(pagination={"skip": 0, "limit": None})
        await router.db_model.all().delete()
        return BaseResponse(data=req)

    @router.post('', summary=f"创建 {model_name} 模型资源", response_model=BaseResponse[schema])
    async def overloaded_create(model: Union[router.create_schema, dict]):
        if isinstance(model, dict):
            req = router.db_model(**model)
        else:
            req = router.db_model(**model.dict())
        await req.save()
        return BaseResponse(data=req)

    @router.get('/{item_id}', summary=f"获取 {model_name} 模型单个资源", response_model=BaseResponse[schema])
    async def overloaded_get_one(item_id: int):
        req = await router.db_model.filter(id=item_id).first()
        if req:
            return BaseResponse(data=req)
        else:
            raise NotFindError

    @router.put('/{item_id}', summary=f"更新 {model_name} 模型单个资源", response_model=BaseResponse[schema])
    async def overloaded_update(item_id: int, model: Union[router.create_schema, dict]):
        if not isinstance(model, dict):
            model = model.dict(exclude_unset=True)
        if not await router.db_model.filter(id=item_id).update(**model):
            raise NotFindError
        req: Model = await router._get_one()(item_id)
        return BaseResponse(data=req)

    @router.delete('/{item_id}', summary=f"删除 {model_name} 模型单个资源", response_model=BaseResponse[schema])
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
