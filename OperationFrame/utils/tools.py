# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2023/05/18
"""
from typing import Union, Type

from tortoise import Model
from tortoise.expressions import Q


def get_model_query_field(model: Type[Model], query) -> list:
    """
    获取模型模糊查询字段
    """
    if hasattr(model.Meta, 'query_fields'):
        query_fields: Union[set, list] = getattr(model.Meta, 'query_fields')
        query_fields = set(query_fields).intersection(model._meta.db_fields)
    else:
        query_fields = model._meta.db_fields

    return [Q(**{f"{x}__icontains": query}) for x in query_fields if not x.startswith('_')]
