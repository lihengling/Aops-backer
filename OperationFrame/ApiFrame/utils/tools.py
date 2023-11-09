# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2023/03/30
"""
import os
from typing import cast, Union, Type, List, Dict
from functools import reduce
from operator import or_
from tortoise import Model

from OperationFrame.ApiFrame.utils.cbv.core import get_cbv_exp


def is_file_changed(file_path: str) -> bool:
    """
    查看文件是否发生变化
    """
    current_stat = os.stat(file_path)
    if current_stat.st_mtime != is_file_changed.previous_stat.st_mtime:
        is_file_changed.previous_stat = current_stat
        return True
    return False


def get_model_pagination(model: Type[Model], pagination: dict, query: Union[str, int] = None):
    """
    获取模型分页处理查询
    """
    skip, limit = pagination.get("skip", 0), pagination.get("limit", None)
    query_model = model.filter(reduce(or_, get_cbv_exp(model, query))) if query is not None else model
    req = query_model.all().offset(cast(int, skip))
    if limit:
        req = req.limit(limit)

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
