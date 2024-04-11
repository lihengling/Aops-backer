# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2023/03/21
"""

from fastapi import Depends
from pydantic.main import ModelMetaclass
from starlette.exceptions import HTTPException
from tortoise import Model
from tortoise.contrib.pydantic import PydanticModel
from tortoise.exceptions import DoesNotExist
from tortoise.queryset import QuerySet

from .base import CBVMetaClass, CBVMeta
from .wrapper import *


class CBV(metaclass=CBVMetaClass):
    """ FastAPI 类路由的实现

    """
    Meta = CBVMeta

    def get_meta(self, key, default=None):
        return getattr(self.Meta, key, getattr(CBVMeta, key, default))

    @property
    def model(self):
        """ 获取 queryset model """
        return self.Meta.model

    @property
    def queryset(self):
        """ 获取 queryset 关联返回外键字段 """
        if self.Meta.queryset:
            queryset = self.model.filter(self.Meta.queryset)
        else:
            queryset = self.model.all()
        # noinspection PyProtectedMember
        return queryset.prefetch_related(*list(self.model._meta.fetch_fields))

    async def fetch_related(self, obj):
        """ 关联查询外键信息 """
        # noinspection PyProtectedMember
        await obj.fetch_related(*list(self.model._meta.fetch_fields))

    @property
    def base_obj_response(self):
        return self.get_meta('base_obj_response')

    @property
    def base_meta_response(self):
        return self.get_meta('base_meta_response')

    @property
    def base_list_data_response(self):
        return self.get_meta('base_list_data_response')

    @property
    def base_list_response(self):
        return self.get_meta('base_list_response')

    @set_meta(META_ANNOTATION, id='base_id_type')
    async def get_obj(self, id) -> Model:
        """ 查询操作对象 """
        try:
            return await self.queryset.get(id=id)
        except DoesNotExist:
            raise HTTPException(status_code=404)

    @set_meta(META_FIELDS, value=True)
    async def apply_filters(self, **kwargs: Dict[str, Any]) -> QuerySet:
        """ 构建query """
        queryset = self.queryset.filter(**{
            key: value for key, value in kwargs.items()
            if value is not None
        })
        # 预加载所有关联外键
        return queryset.prefetch_related(*list(queryset.model._meta.fetch_fields))

    async def apply_sorting(
            self,
            query: QuerySet = Depends(apply_filters)
    ) -> QuerySet:
        """ 构建排序 """
        return query.order_by(*self.get_meta('order_by'))

    async def apply_limit_and_offset(self,
                                     query: QuerySet,
                                     limit: int = None, offset: int = None
                                     ) -> (QuerySet, Meta.base_meta_response):
        """ 构建分页 """
        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)
        return query, self.base_meta_response(limit=limit, offset=offset, total_count=await query.count())

    async def dehydrate(self, obj: Model, method: str = 'get', for_list: bool = False):
        """ 通用序列化数据库模型返回值的方法

        Args:
            obj: 数据库 orm 模型
            method: 请求类型
            for_list: 主键查询 or 批量查询
        """
        if isinstance(obj, Model):
            model: Type[PydanticModel] = self.get_meta(QUERYSET_AUTO_MODEL)
            res = model.from_orm(obj)
        else:
            res = obj

        res = res.__dict__
        res['user'] = 'hahah'
        return res

    async def _post(self, obj: Model = Depends(get_obj)):
        """ 复制对象 """
        obj = await self.post(obj)
        await self.fetch_related(obj)
        return self.base_obj_response(data=await self.dehydrate(obj, method='POST', for_list=False))

    async def post(self, obj: Model):
        model: Type[PydanticModel] = self.get_meta(QUERYSET_AUTO_MODEL_READONLY)
        return await self.model.create(**model.from_orm(obj).dict())

    @set_meta(META_AUTO_MODEL, value=True)
    async def _post_list(self, data: ModelMetaclass):
        """ 创建对象 """
        obj = await self.post_list(data)
        await self.fetch_related(obj)
        return self.base_obj_response(data=await self.dehydrate(obj, method='POST', for_list=False))

    async def post_list(self, data: ModelMetaclass):
        return await self.model.create(**data.dict())

    async def _delete(self, obj: Model = Depends(get_obj)) -> str:
        """ 删除对象 """
        await self.delete(obj)
        return self.base_obj_response()

    async def delete(self, obj: Model):
        await obj.delete()

    async def _delete_list(self, query: QuerySet = Depends(apply_filters)):
        """ 批量删除 """
        await self.delete_list(query)
        return self.base_obj_response()

    async def delete_list(self, query: QuerySet):
        async for obj in query:
            await obj.delete()

    @set_meta(META_AUTO_MODEL, value=True)
    async def _put(self, data: ModelMetaclass, obj: Model = Depends(get_obj)):
        """ 修改对象 """
        obj = await self.put(data, obj)
        await self.fetch_related(obj)
        return self.base_obj_response(data=await self.dehydrate(obj, method='PUT', for_list=False))

    async def put(self, data: ModelMetaclass, obj: Model):
        await obj.update_from_dict(data.dict())
        await obj.save()
        return obj

    @set_meta(META_AUTO_MODEL, value=True)
    async def _put_list(self, data: ModelMetaclass, query: QuerySet = Depends(apply_filters)):
        """ 批量更新 """
        ids = await query.values_list('id', flat=True)
        await self.put_list(data, query)
        objects = [
            await self.dehydrate(obj, method='PUT', for_list=True)
            async for obj in self.queryset.filter(id__in=ids)]
        return self.base_obj_response(data=objects)

    async def put_list(self, data: ModelMetaclass, query: QuerySet):
        async for obj in query:
            await obj.update_from_dict(data.dict())
            await obj.save()

    async def _get(self, obj: Model = Depends(get_obj)):
        """ 主键查询 """
        obj = await self.get(obj)
        return self.base_obj_response(data=await self.dehydrate(obj, method='GET', for_list=False))

    async def get(self, obj: Model):
        return obj

    @set_meta(META_DEFAULT, limit='limit', offset='offset')
    async def _get_list(self,
                        query: QuerySet = Depends(apply_filters),
                        limit: int = None, offset: int = None):
        """ 批量查询 """
        query = await self.get_list(query)
        query = await self.apply_sorting(query)
        query, meta = await self.apply_limit_and_offset(query, limit, offset)

        objects = [
            await self.dehydrate(obj, method='GET', for_list=True)
            async for obj in query]
        print(objects)
        return self.base_list_response(
            data=self.base_list_data_response(meta=meta, objects=objects)
        )

    async def get_list(self, query: QuerySet):
        return query
