# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2023/11/08
"""
from OperationFrame.ApiFrame.apps.rbac.models import User, Role, Permission
from OperationFrame.ApiFrame.base import NotFindError
from OperationFrame.ApiFrame.base.exceptions import ForbiddenError


# 存在用户可操作
async def exists_user(item_id) -> User:
    obj = await User.get_or_none(id=item_id)
    if not obj:
        raise NotFindError

    return obj


# 激活用户可操作
async def active_user(item_id) -> User:
    obj = await exists_user(item_id)

    if not obj.is_active:
        raise ForbiddenError(message='用户为非活跃状态')

    return obj


# 管理员用户不可操作
async def admin_user(item_id) -> User:
    obj = await exists_user(item_id)

    if await obj.is_admin:
        raise ForbiddenError(message='管理员用户不可操作')

    return obj


# 激活\管理员用户不可操作
async def active_admin_user(item_id) -> User:
    obj = await active_user(item_id)

    if await obj.is_admin:
        raise ForbiddenError(message='管理员用户不可操作')

    return obj


# 存在角色可操作
async def exists_role(item_id) -> Role:
    obj = await Role.get_or_none(id=item_id)
    if not obj:
        raise NotFindError

    return obj


# 激活角色可操作
async def active_role(item_id) -> Role:
    obj = await exists_role(item_id)

    if not obj.is_active:
        raise ForbiddenError(message='角色为非活跃状态')

    return obj


# 管理员角色不可操作
async def admin_role(item_id) -> Role:
    obj = await exists_role(item_id)

    if obj.is_admin:
        raise ForbiddenError(message='管理员角色不可操作')

    return obj


# 存在权限可操作
async def exists_permission(item_id) -> Permission:
    obj = await Permission.get_or_none(id=item_id)
    if not obj:
        raise NotFindError

    return obj
