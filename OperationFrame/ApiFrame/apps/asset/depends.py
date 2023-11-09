# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2023/11/09
"""
from OperationFrame.ApiFrame.apps.asset.models import Menu
from OperationFrame.ApiFrame.base import NotFindError


# 存在菜单可操作
async def exists_menu(item_id) -> Menu:
    obj = await Menu.get_or_none(id=item_id)
    if not obj:
        raise NotFindError

    return obj
