# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2023/12/15
"""
from typing import Type, TypeVar

from pydantic.main import validate_model
from tortoise import Model

from OperationFrame.ApiFrame.base.exceptions import BaseValueError, BadRequestError, NotFindError
from OperationFrame.utils.models import BaseModel


class CurdGenerator:
    def __init__(
            self,
            model: Type[Model],
            update_schema: Type[BaseModel] = None,
            create_schema: Type[BaseModel] = None,
            pk: str = 'id'):
        self.model = model
        self.update_schema = update_schema
        self.create_schema = create_schema
        self.pk = pk

    @staticmethod
    def format_schema(schema: BaseModel, schema_type: Type[BaseModel]) -> dict:
        if schema_type is None:
            raise BadRequestError(message=f"更新请求结构 {schema_type} 未定义")

        if isinstance(schema, schema_type):
            schema = schema.dict()
        elif isinstance(schema, dict):
            _, _, failed = validate_model(schema_type, schema)
            if failed is not None:
                raise BaseValueError(message=f'{failed}')
        else:
            raise BaseValueError

        return schema

    async def update_item(self, schema: BaseModel) -> TypeVar:
        schema = self.format_schema(schema, self.update_schema)
        schema_id = schema.pop(self.pk, 0)
        obj = await self.model.get_or_none(**{f'{self.pk}': schema_id})
        if not obj:
            raise BaseValueError(message=f"主键 {self.pk} 或 {schema_id} 不存在")

        try:
            await obj.update_from_dict(schema)
            await obj.save()
            return obj
        except Exception as err:
            raise BaseValueError(message=f"更新失败 | {err}")

    async def create_item(self, schema: BaseModel) -> TypeVar:
        schema = self.format_schema(schema, self.create_schema)

        try:
            obj = await self.model.create(**schema)
            return obj
        except Exception as err:
            raise BaseValueError(message=f"新建失败 | {err}")

    async def delete_item(self, item_id) -> TypeVar:
        obj = await self.model.get_or_none(id=item_id)
        if not obj:
            raise NotFindError

        try:
            await obj.delete()
            return obj
        except Exception as err:
            raise BaseValueError(message=f"删除失败 | {err}")
