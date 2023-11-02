# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2023/03/07
"""
from typing import Union, List
from fastapi import Depends
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

from OperationFrame.ApiFrame.apps.asset.models import Department, Menu
from OperationFrame.ApiFrame.apps.rbac.models import User, Role, Permission
from OperationFrame.ApiFrame.apps.rbac.schema import UserAuthResponse, UserAuthRequest, get_user_response, \
    UserListResponse, UserInfoResponse, UserUpdateRequest, UserBase, UserCreateRequest, RoleListResponse, \
    RoleInfoResponse, RoleBase, RoleCreateRequest, RoleUpdateRequest, PermissionListResponse, PermissionInfoResponse, \
    PermissionBase, PermissionCreateRequest, PermissionUpdateRequest
from OperationFrame.ApiFrame.base import router_user, ORJSONResponse, constant, router_role, router_permission
from OperationFrame.ApiFrame.base.exceptions import AccessTokenExpire, BadRequestError, NotFindError, ForbiddenError, \
    BaseValueError
from OperationFrame.ApiFrame.utils.tools import get_model_pagination
from OperationFrame.config import config
from OperationFrame.config.constant import ENV_DEV
from OperationFrame.lib.depend import paginate_factory
from OperationFrame.utils.models import BaseResponse, BaseResponseList
from OperationFrame.ApiFrame.utils.jwt import create_token


# user 模型接口
if config.ENV == ENV_DEV:
    @router_user.post("/token", summary="docs 获取 token，仅用于开发环境测试")
    async def login_oauth(data: OAuth2PasswordRequestForm = Depends()):
        user = await User.filter(username=data.username).first()
        jwt_token = create_token(data={
            "username": user.username,
            "password": user.get_password(data.password)
        })

        return {'access_token': jwt_token, 'token_type': constant.JWT_TOKEN_TYPE}


@router_user.post("/register", summary="用户注册", response_model=BaseResponse[UserAuthResponse])
async def register(data: UserAuthRequest) -> ORJSONResponse:
    if await User.filter(username=data.username).exists():
        raise BadRequestError(message=f'user {data.username} is exists')

    user = await User.create(username=data.username, password=User.get_password(data.password))
    if not await Role.exists():
        role = await Role.create(name='admin', role_name='管理员', is_admin=True,
                                 description='拥有所有权限')
        await user.role.add(role)
    return await get_user_response(user)


@router_user.post("/login", summary="用户登录", response_model=BaseResponse[UserAuthResponse])
async def login(data: UserAuthRequest) -> ORJSONResponse:
    user = await User.get_or_none(username=data.username)
    if not user or not user.check_password(data.password) and user.is_active:
        raise AccessTokenExpire()

    token = create_token(data={
        "username": user.username,
        "password": user.get_password(data.password)
    })
    rsp = await get_user_response(user, token=token)
    rsp.set_cookie('token', token, expires=constant.JWT_TOKEN_MAX_AGE.total_seconds())
    rsp.set_cookie('username', user.username, expires=constant.JWT_TOKEN_MAX_AGE.total_seconds())
    return rsp


@router_user.get('', summary='获取用户列表', response_model=BaseResponseList[List[UserListResponse]])
async def user_list(pagination: dict = paginate_factory(), query: Union[str, int] = None):
    req = get_model_pagination(User, pagination, query)
    data = [
        dict(id=x.id, username=x.username, is_admin=await x.is_admin, is_active=x.is_active,
             department=await x.department_name) for x in await req
    ]

    return BaseResponseList(data=data, total=await User.filter().count())


@router_user.get('/{item_id}', summary='获取用户信息', response_model=BaseResponse[UserInfoResponse])
async def user_info(item_id: int):
    user = await User.get_or_none(id=item_id)
    if user:
        roles = [{'id': role.id, 'role_name': role.role_name, 'description': role.description} for role in await user.role]
        menus = [{'id': menu.id, 'menu_name': menu.menu_name, 'url': menu.url} for menu in await user.menus]
        dep = await user.department
        department = {'id': dep.id, 'department_name': dep.department_name} if dep else {}
        return BaseResponse(data=dict(id=user.id, is_admin=await user.is_admin, department=department,
                            username=user.username, is_active=user.is_active, roles=roles, menus=menus))
    else:
        raise NotFindError


@router_user.delete('/{item_id}', summary='删除用户', response_model=BaseResponse[UserBase])
async def user_delete(item_id: int):
    user = await User.get_or_none(id=item_id)
    if not user:
        raise NotFindError

    if await user.is_admin:
        raise ForbiddenError(message='管理员用户不可删除')
    else:
        await user.delete()
        return BaseResponse(data=UserBase(username=user.username, is_active=user.is_active))


@router_user.post('', summary='新增用户', response_model=BaseResponse[UserBase])
async def user_create(user_schema: UserCreateRequest):
    if not isinstance(user_schema, dict):
        user_dict = user_schema.dict(exclude_unset=True)
    else:
        user_dict = user_schema

    roles:        list = user_dict.pop('role_id')
    menus:        list = user_dict.pop('menu_id')
    department_id: int = user_dict.pop('department_id')

    # 检查用户参数
    if not await Department.filter(id=department_id).exists():
        raise BaseValueError(message=f'部门id: {department_id} 不存在')

    if await User.filter(username=user_dict['username']).exists():
        raise BaseValueError(message=f"用户: {user_dict['username']} 已存在")

    # 创建本表
    user = await User.create(username=user_dict['username'], password=User.get_password(user_dict['password']),
                             department_id=department_id)

    # 创建用户角色
    role_objs = [x for x in await Role.filter(id__in=roles).all()]
    for role_obj in role_objs:
        await user.role.add(role_obj)

    # 创建用户菜单
    menu_objs = [x for x in await Menu.filter(id__in=menus).all()]
    for menu_obj in menu_objs:
        await user.menus.add(menu_obj)

    return BaseResponse(data=UserBase(username=user.username, is_active=user.is_active))


@router_user.put('/{item_id}', summary='修改用户信息', response_model=BaseResponse[UserBase])
async def user_update(item_id: int, user_schema: UserUpdateRequest):
    if not isinstance(user_schema, dict):
        user_dict = user_schema.dict(exclude_unset=True)
    else:
        user_dict = user_schema

    roles:        list = user_dict.pop('role_id')
    menus:        list = user_dict.pop('menu_id')
    department_id: int = user_dict.pop('department_id')

    user = await User.get_or_none(id=item_id)
    if not user:
        raise NotFindError

    if await user.is_admin:
        raise ForbiddenError(message='管理员用户不可修改')

    # 更新用户部门
    department_obj = await Department.get_or_none(id=department_id)
    if not department_obj:
        raise BaseValueError(message=f'部门id: {department_id} 不存在')
    user.department = department_obj

    # 更新本表
    await user.update_from_dict(user_dict)

    # 更新用户角色
    await user.role.clear()
    role_objs = [x for x in await Role.filter(id__in=roles).all()]
    for role_obj in role_objs:
        await user.role.add(role_obj)

    # 更新用户菜单
    await user.menus.clear()
    menu_objs = [x for x in await Menu.filter(id__in=menus).all()]
    for menu_obj in menu_objs:
        await user.menus.add(menu_obj)

    # 保存信息
    await user.save()

    return BaseResponse(data=UserBase(username=user.username, is_active=user.is_active))


# role 模型接口
@router_role.get('', summary='获取角色列表', response_model=BaseResponseList[List[RoleListResponse]])
async def role_list(pagination: dict = paginate_factory(), query: Union[str, int] = None):
    req = get_model_pagination(Role, pagination, query)
    data = [
        dict(id=x.id, role_name=x.role_name, is_admin=x.is_admin, is_active=x.is_active,
             description=x.description) for x in await req
    ]

    return BaseResponseList(data=data, total=await Role.filter().count())


@router_role.get('/{item_id}', summary='获取角色信息', response_model=BaseResponse[RoleInfoResponse])
async def role_info(item_id: int):
    role = await Role.get_or_none(id=item_id)
    if role:
        permissions = [{'id': menu.id, 'permission_name': menu.permission_name} for menu in await role.permission]
        return BaseResponse(data=dict(id=role.id, is_admin=role.is_admin,  is_active=role.is_active,
                                      role_name=role.role_name, permissions=permissions, description=role.description))
    else:
        raise NotFindError


@router_role.delete('/{item_id}', summary='删除角色', response_model=BaseResponse[RoleBase])
async def role_delete(item_id: int):
    role = await Role.get_or_none(id=item_id)
    if not role:
        raise NotFindError

    if role.is_admin:
        raise ForbiddenError(message='管理员角色不可删除')
    else:
        await role.delete()
        return BaseResponse(data=RoleBase(role_name=role.role_name, is_active=role.is_active))


@router_role.post('', summary='新增角色', response_model=BaseResponse[RoleBase])
async def role_create(role_schema: RoleCreateRequest):
    if not isinstance(role_schema, dict):
        role_dict = role_schema.dict(exclude_unset=True)
    else:
        role_dict = role_schema

    permission_id: int = role_dict.pop('permission_id')

    # 检查参数
    if await Role.filter(role_name=role_dict['role_name']).exists():
        raise BaseValueError(message=f"角色: {role_dict['role_name']} 已存在")

    # 创建本表
    role = await Role.create(role_name=role_dict['role_name'], is_active=role_dict['is_active'],
                             description=role_dict['description'])

    # 创建角色权限
    permission_objs = [x for x in await Permission.filter(id__in=permission_id).all()]
    for permission_obj in permission_objs:
        await role.permission.add(permission_obj)

    return BaseResponse(data=RoleBase(role_name=role.role_name, is_active=role.is_active))


@router_role.put('/{item_id}', summary='修改角色信息', response_model=BaseResponse[RoleBase])
async def role_update(item_id: int, role_schema: RoleUpdateRequest):
    if not isinstance(role_schema, dict):
        role_dict = role_schema.dict(exclude_unset=True)
    else:
        role_dict = role_schema

    permission_id: int = role_dict.pop('permission_id')

    role = await Role.get_or_none(id=item_id)
    if not role:
        raise NotFindError

    if role.is_admin:
        raise ForbiddenError(message='管理员角色不可修改')

    # 更新本表
    await role.update_from_dict(role_dict)

    # 更新角色权限
    await role.permission.clear()
    permission_objs = [x for x in await Permission.filter(id__in=permission_id).all()]
    for permission_obj in permission_objs:
        await role.permission.add(permission_obj)

    # 保存信息
    await role.save()

    return BaseResponse(data=RoleBase(role_name=role.role_name, is_active=role.is_active))


# permission 模型接口
@router_permission.get('', summary='获取权限列表', response_model=BaseResponseList[List[PermissionListResponse]])
async def permission_list(pagination: dict = paginate_factory(), query: Union[str, int] = None):
    req = get_model_pagination(Permission, pagination, query)
    data = [
        dict(id=x.id, permission_name=x.permission_name, is_active=x.is_active, description=x.description)
        for x in await req
    ]

    return BaseResponseList(data=data, total=await Permission.filter().count())


@router_permission.get('/{item_id}', summary='获取权限信息', response_model=BaseResponse[PermissionInfoResponse])
async def permission_info(item_id: int):
    permission = await Permission.get_or_none(id=item_id)
    if permission:
        roles = [{'id': role.id, 'role_name': role.role_name} for role in await permission.role]
        return BaseResponse(data=dict(id=permission.id, is_active=permission.is_active, roles=roles,
                                      description=permission.description, permission_name=permission.permission_name))
    else:
        raise NotFindError


@router_permission.delete('/{item_id}', summary='删除权限', response_model=BaseResponse[PermissionBase])
async def permission_delete(item_id: int):
    permission = await Permission.get_or_none(id=item_id)
    if not permission:
        raise NotFindError

    await permission.delete()
    return BaseResponse(data=PermissionBase(permission_name=permission.permission_name, is_active=permission.is_active))


@router_permission.post('', summary='新增权限', response_model=BaseResponse[PermissionBase])
async def permission_create(permission_schema: PermissionCreateRequest):
    if not isinstance(permission_schema, dict):
        permission_dict = permission_schema.dict(exclude_unset=True)
    else:
        permission_dict = permission_schema

    # 检查参数
    if await Permission.filter(permission_name=permission_dict['permission_name']).exists():
        raise BaseValueError(message=f"权限: {permission_dict['permission_name']} 已存在")

    # 创建本表
    permission = await Permission.create(permission_name=permission_dict['permission_name'],
                                         is_active=permission_dict['is_active'],
                                         description=permission_dict['description'])

    return BaseResponse(data=PermissionBase(permission_name=permission.permission_name, is_active=permission.is_active))


@router_permission.put('/{item_id}', summary='修改权限信息', response_model=BaseResponse[PermissionBase])
async def permission_update(item_id: int, permission_schema: PermissionUpdateRequest):
    if not isinstance(permission_schema, dict):
        permission_dict = permission_schema.dict(exclude_unset=True)
    else:
        permission_dict = permission_schema

    permission = await Permission.get_or_none(id=item_id)
    if not permission:
        raise NotFindError

    # 更新本表
    await permission.update_from_dict(permission_dict)

    # 保存信息
    await permission.save()

    return BaseResponse(data=PermissionBase(permission_name=permission.permission_name, is_active=permission.is_active))
