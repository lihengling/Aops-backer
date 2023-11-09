"""
Author: 'LingLing'
Date: 2023/11/08
"""
from typing import List, Dict, Union

from OperationFrame.ApiFrame.apps.asset.models import Department
from OperationFrame.ApiFrame.utils.tools import get_model_pagination, build_foreignKey_tree


# 完整部门树
async def full_department_tree(pagination: dict, query: Union[str, int] = None) -> List[Dict]:
    objs = get_model_pagination(Department, pagination, query)
    objs = await objs
    obj_list = [{'id': x.id, 'department_name': x.department_name, 'parent_id': x.parent_id} for x in objs]
    return build_foreignKey_tree(obj_list)
