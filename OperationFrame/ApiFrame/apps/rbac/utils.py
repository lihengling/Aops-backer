# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2023/11/08
"""
from typing import List, Dict, Union
from tortoise.expressions import Q

from OperationFrame.ApiFrame.apps.asset.models import Menu
from OperationFrame.ApiFrame.apps.rbac.models import User
from OperationFrame.ApiFrame.utils.tools import get_model_pagination, build_foreignKey_tree


# 完整菜单树
async def full_menu_tree(pagination: dict, query: Union[str, int] = None) -> List[Dict]:
    objs = get_model_pagination(Menu, pagination, query)
    objs = await objs
    obj_list = [{'id': x.id, 'menu_name': x.menu_name, 'url': x.url, 'parent_id': x.parent_id} for x in objs]
    return build_foreignKey_tree(obj_list)


# 用户菜单树
async def user_menu_tree(user: User) -> List[Dict]:
    objs = await user.menu if not await user.is_admin else await Menu.all()
    obj_list = [{'id': x.id, 'menu_name': x.menu_name, 'url': x.url, 'parent_id': x.parent_id} for x in objs]
    return build_foreignKey_tree(obj_list)


# id菜单树
async def id_menu_tree(item_id: int) -> List[Dict]:
    objs = await Menu.filter(Q(id=item_id) | Q(parent_id=item_id)).all()
    obj_list = [{'id': x.id, 'menu_name': x.menu_name, 'url': x.url, 'parent_id': x.parent_id} for x in objs]
    return build_foreignKey_tree(obj_list)
