"""
Author: 'LingLing'
Date: 2023/11/08
"""
from typing import List, Dict, Union

from tortoise.expressions import Q

from OperationFrame.ApiFrame.apps.asset.models import Department
from OperationFrame.ApiFrame.utils.tools import get_model_pagination, build_foreignKey_tree


# 完整部门树
async def full_department_tree(pagination: dict, query: Union[str, int] = None) -> List[Dict]:
    objs = get_model_pagination(Department, pagination, query)
    objs = await objs
    obj_list = [{'id': x.id, 'department_name': x.department_name, 'parent_id': x.parent_id} for x in objs]
    return build_foreignKey_tree(obj_list)


# id菜单树
async def id_department_tree(item_id: int) -> List[Dict]:
    while True:
        res = await Department.filter(id=item_id).first()
        if not res.parent_id:
            item_id = res.id
            break
        else:
            item_id = res.parent_id

    objs = await Department.filter(Q(id=item_id) | Q(parent_id=item_id)).all()
    obj_list = [{'id': x.id, 'department_name': x.department_name, 'parent_id': x.parent_id} for x in objs]
    return build_foreignKey_tree(obj_list)
