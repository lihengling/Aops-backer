# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2023/03/30
"""
from typing import Type, List, Dict
from functools import reduce
from operator import or_
from tortoise import Model

from OperationFrame.lib.depend import PageQuery
from OperationFrame.utils.tools import get_model_query_field


def get_model_pagination(model: Type[Model], pq: PageQuery):
    """
    获取模型分页处理查询
    """
    query_model = model.filter(reduce(or_, get_model_query_field(model, pq.query))) if pq.query else model
    req = query_model.all().limit(pq.pageSize).offset((pq.pageIndex - 1) * pq.pageSize)
    return req


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
