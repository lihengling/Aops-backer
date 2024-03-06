# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2023/03/07
"""
from typing import List
from fastapi import Depends, Security, Query
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

from OperationFrame.ApiFrame.apps.asset.models import Menu
from OperationFrame.ApiFrame.apps.rbac.models import User, Role, Permission
from OperationFrame.ApiFrame.apps.rbac.schema import UserAuthResponse, UserAuthRequest, get_user_response, \
    UserListResponse, UserUpdateRequest, UserBase, UserCreateRequest, RoleListResponse, \
    RoleBase, RoleCreateRequest, RoleUpdateRequest, PermissionListResponse, PermissionBase, PermissionCreateRequest, \
    PermissionUpdateRequest, UserMenuResponse, get_role_response, get_permission_response
from OperationFrame.ApiFrame.apps.rbac.utils import user_menu_tree
from OperationFrame.ApiFrame.base import router_user, ORJSONResponse, constant, router_role, router_permission, \
    PERMISSION_INFO, PERMISSION_DELETE, PERMISSION_CREATE, PERMISSION_UPDATE
from OperationFrame.ApiFrame.base.exceptions import AccessTokenExpire, BadRequestError, ForbiddenError
from OperationFrame.ApiFrame.utils.curd import CurdGenerator
from OperationFrame.ApiFrame.utils.tools import get_model_pagination
from OperationFrame.config import config
from OperationFrame.config.constant import ENV_DEV
from OperationFrame.lib.depend import PageQuery
from OperationFrame.utils.models import BaseResponse, BaseResponseList
from OperationFrame.ApiFrame.utils.jwt import create_token, check_permissions

# 初始化 curd
curd_role:       CurdGenerator = CurdGenerator(Role, RoleUpdateRequest, RoleCreateRequest)
curd_user:       CurdGenerator = CurdGenerator(User, UserUpdateRequest, UserUpdateRequest)
curd_permission: CurdGenerator = CurdGenerator(Permission, PermissionUpdateRequest, PermissionCreateRequest)

# user 模型接口
if config.ENV == ENV_DEV:
    @router_user.post("/token/", summary="docs 获取 token，仅用于开发环境测试")
    async def login_oauth(data: OAuth2PasswordRequestForm = Depends()):
        user = await User.filter(username=data.username).first()
        jwt_token = create_token(data={
            "username": user.username,
            "password": user.get_password(data.password)
        })

        return {'access_token': jwt_token, 'token_type': constant.JWT_TOKEN_TYPE}


@router_user.post("/register/", summary="用户注册", response_model=BaseResponse[UserAuthResponse])
async def register(data: UserAuthRequest) -> ORJSONResponse:
    if await User.filter(username=data.username).exists():
        raise BadRequestError(message=f'user {data.username} is exists')

    user = await User.create(username=data.username, password=User.get_password(data.password))
    if not await Role.exists():
        await Role.create(name='base_admin', role_name='普通管理员', is_admin=False, description='拥有分配到的资源所有权限')
        await Role.create(name='base_user', role_name='基础用户', is_admin=False, description='拥有基础权限')
        role = await Role.create(name='admin', role_name='管理员', is_admin=True,
                                 description='拥有所有权限')
        await user.role.add(role)

    # 赋予基础权限
    if not await user.is_admin:
        base_role = await Role.filter(name='base_user', is_active=True).first()
        if base_role:
            await user.role.add(base_role)

    return await get_user_response(user)


@router_user.post("/login/", summary="用户登录", response_model=BaseResponse[UserAuthResponse])
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


@router_user.get('/list/', summary='获取用户列表', response_model=BaseResponseList[List[UserListResponse]],
                 dependencies=[Security(check_permissions, scopes=[f'user_{PERMISSION_INFO}'])])
async def user_list(pq: PageQuery = Depends(PageQuery)):
    objs = get_model_pagination(User, pq)
    data = []
    for x in await objs:
        user_data = dict(id=x.id, username=x.username, is_admin=await x.is_admin, is_active=x.is_active,
                 department=await x.department_name, created_at=x.created_at, role=[])
        for i in await x.role:
            user_data['role'].append(dict(name=i.name, role_name=i.role_name, description=i.description,
                             is_active=i.is_active, is_admin=i.is_admin))

            user_data['menu'] = await user_menu_tree(x)
        data.append(user_data)
    return BaseResponseList(data=data, total=await User.filter().count())


@router_user.delete('/', summary='删除用户', response_model=BaseResponse[UserBase],
                 dependencies=[Security(check_permissions, scopes=[f'user_{PERMISSION_DELETE}'])])
async def user_delete(schema: int = Query(..., description='主键id', gt=0, alias='id')):
    return get_user_response(await curd_user.delete_item(schema))


@router_user.post('/', summary='新增用户', response_model=BaseResponse[UserBase],
                 dependencies=[Security(check_permissions, scopes=[f'user_{PERMISSION_CREATE}'])])
async def user_create(schema: UserCreateRequest):
    return get_user_response(await curd_user.create_item(schema))


@router_user.put('/', summary='修改用户信息', response_model=BaseResponse[UserBase],
                 dependencies=[Security(check_permissions, scopes=[f'user_{PERMISSION_UPDATE}'])])
async def user_update(schema: UserUpdateRequest):
    obj = await curd_user.update_item(schema)
    # 更新用户菜单
    await obj.menu.clear()
    menu_objs = [x for x in await Menu.filter(id__in=schema.menu_id).all()]
    for menu_obj in menu_objs:
        await obj.menu.add(menu_obj)

    return get_user_response(obj)


@router_user.get('/menu/', summary='用户菜单', response_model=BaseResponse[UserMenuResponse],
                 dependencies=[Security(check_permissions)])
async def user_menu(schema: int = Query(..., description='主键id', gt=0, alias='id')):
    obj = await User.get_or_none(id=schema)

    if not obj.is_active:
        raise ForbiddenError(message='用户为非活跃状态')

    menus = await user_menu_tree(obj)
    return BaseResponse(data=UserMenuResponse(username=obj.username, is_active=obj.is_active, menus=menus))


# role 模型接口
@router_role.get('/list/', summary='获取角色列表', response_model=BaseResponseList[List[RoleListResponse]],
                 dependencies=[Security(check_permissions, scopes=[f'role_{PERMISSION_INFO}'])])
async def role_list(pq: PageQuery = Depends(PageQuery)):
    objs = get_model_pagination(Role, pq)
    data = [dict(id=x.id, name=x.name, role_name=x.role_name, is_admin=x.is_admin, is_active=x.is_active,
                 description=x.description, permissions=
                 [{'id': x.id, 'permission_name': x.permission_name, 'description': x.description,
                   'is_active': x.is_active} for x in (await Permission.all() if x.is_admin
                   else await x.permission)]) for x in await objs]

    return BaseResponseList(data=data, total=await Role.filter().count())


@router_role.delete('/', summary='删除角色', response_model=BaseResponse[RoleBase],
                 dependencies=[Security(check_permissions, scopes=[f'role_{PERMISSION_DELETE}'])])
async def role_delete(schema: int = Query(..., description='主键id', gt=0, alias='id')):
    return get_role_response(await curd_role.delete_item(schema))


@router_role.post('/', summary='新增角色', response_model=BaseResponse[RoleBase],
                 dependencies=[Security(check_permissions, scopes=[f'role_{PERMISSION_CREATE}'])])
async def role_create(schema: RoleCreateRequest):
    # 更新本表
    role = await curd_role.create_item(schema)

    # 更新链表
    if not role.is_admin:
        await role.permission.clear()
        permission_objs = [x for x in await Permission.filter(id__in=schema.permission_id).all()]
        for permission_obj in permission_objs:
            await role.permission.add(permission_obj)

    return get_role_response(role)


@router_role.put('/', summary='修改角色信息', response_model=BaseResponse[RoleBase],
                 dependencies=[Security(check_permissions, scopes=[f'role_{PERMISSION_UPDATE}'])])
async def role_update(schema: RoleUpdateRequest):
    # 更新本表
    role = await curd_role.update_item(schema)

    # 更新链表
    if not role.is_admin:
        await role.permission.clear()
        permission_objs = [x for x in await Permission.filter(id__in=schema.permission_id).all()]
        for permission_obj in permission_objs:
            await role.permission.add(permission_obj)

    return get_role_response(role)


# permission 模型接口
@router_permission.get('/list/', summary='获取权限列表', response_model=BaseResponseList[List[PermissionListResponse]],
                    dependencies=[Security(check_permissions, scopes=[f'permission_{PERMISSION_INFO}'])])
async def permission_list(pq: PageQuery = Depends(PageQuery)):
    objs = get_model_pagination(Permission, pq)
    data = [dict(id=x.id, permission_name=x.permission_name, is_active=x.is_active, description=x.description)
            for x in await objs]
    return BaseResponseList(data=data, total=await Permission.filter().count())


@router_permission.delete('/', summary='删除权限', response_model=BaseResponse[PermissionBase],
                    dependencies=[Security(check_permissions, scopes=[f'permission_{PERMISSION_DELETE}'])])
async def permission_delete(schema: int = Query(..., description='主键id', gt=0, alias='id')):
    return get_permission_response(await curd_permission.delete_item(schema))


@router_permission.post('/', summary='新增权限', response_model=BaseResponse[PermissionBase],
                    dependencies=[Security(check_permissions, scopes=[f'permission_{PERMISSION_CREATE}'])])
async def permission_create(schema: PermissionCreateRequest):
    return get_permission_response(await curd_permission.create_item(schema))


@router_permission.put('/', summary='修改权限信息', response_model=BaseResponse[PermissionBase],
                    dependencies=[Security(check_permissions, scopes=[f'permission_{PERMISSION_UPDATE}'])])
async def permission_update(schema: PermissionUpdateRequest):
    return get_permission_response(await curd_permission.update_item(schema))
