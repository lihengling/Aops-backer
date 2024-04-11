# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2024/03/12
"""
from typing import List, Any
from fastapi import APIRouter, Depends
from tortoise import Model

from OperationFrame.ApiFrame.base import NotFindError
from OperationFrame.ApiFrame.utils.modelView.tool import build_foreignKey_tree, get_model_pagination
from OperationFrame.lib.depend import PageQuery
from OperationFrame.utils.models import BaseResponseList, BaseResponse, BaseModel


class modelView:
    """
    多级视图基类，请根据如下配置对接口进行定制
    param:
        mounted: - bool - 是否挂载路由，如果设置为 False，该视图接口将不注册到 app，默认为：True
        router: - router_obj - 路由对象，承载接口的路由对象，请提供 fastapi 的路由对象
        response_model: 响应模型，提供接口的基础响应/返回模型
        depends: - list - 依赖模型，若定义了此依赖，将会在接口运行时执                                                    行
        querySet: - Model_obj - tortoise 模型对象，用于数据库io操作
        methods: - list - 接口提供的方法，默认提供 5 个通用接口
        permissions: - list - 接口访问所需的权限列表
        fields: - set - 响应模型返回的字符串，默认全部返回
        update_schema: - BaseModel - 更新数据所需的数据模型，需要定义后才能注册 post 方法
        create_schema: - BaseModel - 创建数据所需的数据模型，需要定义后才能注册 put 方法
    extra:
        action 装饰器允许在类 cbv 视图中注册额外的接口
    """
    mounted:            bool = True
    router:        APIRouter = None
    response_model:     List = []
    depends:            List = []
    querySet:          Model = None
    methods:       List[str] = ['GET', 'POST', 'PUT', 'DELETE', 'OPTION']
    permissions:   List[str] = []
    fields:              set = {}
    update_schema: BaseModel = None
    create_schema: BaseModel = None

    async def get_list(self, query: PageQuery = Depends(PageQuery)) -> BaseResponseList[Any]:
        objs = get_model_pagination(self.querySet, query)
        obj_list = [filter_field(x, self.fields) for x in await objs]
        obj_list = build_foreignKey_tree(obj_list) if query.query is None else obj_list

        return BaseResponseList(data=obj_list, total=await self.querySet.filter().count())

    async def get(self, id: int):
        obj = await self.querySet.get_or_none(id=id)
        if not obj:
            raise NotFindError

        return BaseResponse(data=filter_field(obj, self.fields))

    async def post(self, id: int):
        return {'hello': f'world post {id}'}

    async def put(self, id: int):
        return {'hello': f'world put {id}'}

    async def delete(self, id: int):
        return {'hello': f'world delete {id}'}


def filter_field(obj, fields):
    return {field: getattr(obj, field, None) for field in fields}
