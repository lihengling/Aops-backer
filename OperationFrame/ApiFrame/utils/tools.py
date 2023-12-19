# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2023/03/30
"""
import os
from typing import Type, List, Dict
from functools import reduce
from operator import or_
from tortoise import Model

from OperationFrame.lib.depend import PageQuery
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


def get_model_pagination(model: Type[Model], pq: PageQuery):
    """
    获取模型分页处理查询
    """
    query_model = model.filter(reduce(or_, get_cbv_exp(model, pq.query))) if pq.query else model
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
