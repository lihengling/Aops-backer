# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2023/11/08
"""
from typing import List, Dict

from OperationFrame.ApiFrame.apps.asset.models import Menu


# 用户获取菜单树
async def user_menu_tree(user) -> List[Dict]:
    menu_objs = await Menu.all() if await user.is_admin else await user.menu
    menu_list = [{'id': x.id, 'menu_name': x.menu_name, 'url': x.url, 'parent_id': x.parent_id} for x in menu_objs]

    def build_menu_tree(menus, parent_id: int = None):
        menu_tree = []
        for menu in menus:
            if menu['parent_id'] == parent_id:
                children = build_menu_tree(menus, menu['id'])
                if children:
                    menu['children'] = children
                menu_tree.append(menu)
        return menu_tree

    return build_menu_tree(menu_list)
