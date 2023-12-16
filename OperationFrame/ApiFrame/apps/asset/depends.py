# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2023/11/09
"""
from OperationFrame.ApiFrame.apps.asset.models import Menu, Department
from OperationFrame.ApiFrame.base import NotFindError


# 存在部门可操作
async def exists_department(item_id) -> Department:
    obj = await Department.get_or_none(id=item_id)
    if not obj:
        raise NotFindError

    return obj
