# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2023/11/08
"""
from typing import List, Dict

from OperationFrame.lib.depend import PageQuery
from OperationFrame.ApiFrame.apps.asset.models import Menu
from OperationFrame.ApiFrame.apps.rbac.models import User
from OperationFrame.ApiFrame.utils.tools import get_model_pagination, build_foreignKey_tree


# 完整菜单树
async def full_menu_tree(pq: PageQuery) -> List[Dict]:
    objs = get_model_pagination(Menu, pq)
    obj_list = [{'id': x.id, 'menu_name': x.menu_name, 'is_show': x.is_show, 'parent_id': x.parent_id,
                 'icon': x.icon, 'path': x.path, 'frame_url': x.frame_url, 'sort': x.sort, 'component': x.component,
                 'menu_title': x.menu_title, 'is_active': x.is_active, 'is_cache': x.is_cache, 'redirect': x.redirect,
                 'is_menu': x.is_menu}
                for x in await objs]
    return build_foreignKey_tree(obj_list) if pq.query is None else obj_list


# 用户菜单树
async def user_menu_tree(user: User) -> List[Dict]:
    objs = await user.menu if not await user.is_admin else await Menu.all()
    obj_list = [{'id': x.id, 'menu_name': x.menu_name, 'is_show': x.is_show, 'parent_id': x.parent_id,
                 'icon': x.icon, 'path': x.path, 'sort': x.sort, 'is_cache': x.is_cache, 'frame_url': x.frame_url,
                 'component': x.component, 'menu_title': x.menu_title, 'is_active': x.is_active, 'redirect': x.redirect,
                 'is_menu': x.is_menu}
                for x in objs]
    return build_foreignKey_tree(obj_list)
