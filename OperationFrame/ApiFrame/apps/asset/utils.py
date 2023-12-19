"""
Author: 'LingLing'
Date: 2023/11/08
"""
from typing import List, Dict

from OperationFrame.lib.depend import PageQuery
from OperationFrame.ApiFrame.apps.asset.models import Department
from OperationFrame.ApiFrame.utils.tools import get_model_pagination, build_foreignKey_tree


# 完整部门树
async def full_department_tree(pq: PageQuery) -> List[Dict]:
    objs = get_model_pagination(Department, pq)
    obj_list = [{'id': x.id, 'department_name': x.department_name, 'parent_id': x.parent_id, 'is_active': x.is_active,
                 'description': x.description, 'created_at': x.created_at}
                for x in await objs]
    return build_foreignKey_tree(obj_list) if pq.query is None else obj_list
