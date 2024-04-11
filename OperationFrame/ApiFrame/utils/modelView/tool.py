# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2024/03/18
"""
from typing import Type, List, Dict
from functools import reduce
from operator import or_


from tortoise import Model
from tortoise.expressions import Q

from OperationFrame.lib.depend import PageQuery


def get_model_pagination(model: Model, query: PageQuery):
    """
    获取模型分页处理查询
    """
    query_model = model.filter(reduce(or_, get_model_query_field(model, query.query))) if query.query else model
    return query_model.all().limit(query.pageSize).offset((query.pageIndex - 1) * query.pageSize)


def get_model_query_field(model: Model, query: any) -> list:
    """
    获取模型模糊查询字段
    """
    query_fields = model._meta.db_fields if not hasattr(model.Meta, 'query_fields') else \
        set(getattr(model.Meta, 'query_fields', [])).intersection(model._meta.db_fields)
    return [Q(**{f"{x}__icontains": query}) for x in query_fields if not x.startswith('_')]


def build_foreignKey_tree(objs, parent_id: int = None) -> List[Dict]:
    """
    构建外键层级树,
    注意：外键必须命名为 parent_id
    """
    obj_tree = []
    for obj in objs:
        if obj['parent_id'] == parent_id:
            children = build_foreignKey_tree(objs, obj['id'])
            if children:
                obj['children'] = children
            obj_tree.append(obj)
    return obj_tree
