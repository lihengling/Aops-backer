# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2023/03/07
"""
from typing import Union, List, Type
from fastapi import Depends, Security
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

from OperationFrame.ApiFrame.apps.asset.models import Department, Menu
from OperationFrame.ApiFrame.apps.rbac.models import User, Role, Permission
from OperationFrame.ApiFrame.apps.rbac.schema import UserAuthResponse, UserAuthRequest, get_user_response, \
    UserListResponse, UserInfoResponse, UserUpdateRequest, UserBase, UserCreateRequest, RoleListResponse, \
    RoleInfoResponse, RoleBase, RoleCreateRequest, RoleUpdateRequest, PermissionListResponse, PermissionInfoResponse, \
    PermissionBase, PermissionCreateRequest, PermissionUpdateRequest, UserMenuResponse, UserMenuUpdateRequest
from OperationFrame.ApiFrame.apps.rbac.depends import active_user, exists_user, admin_user, \
    active_admin_user, exists_role, admin_role, exists_permission
from OperationFrame.ApiFrame.apps.rbac.utils import user_menu_tree
from OperationFrame.ApiFrame.base import router_user, ORJSONResponse, constant, router_role, router_permission, \
    PERMISSION_INFO, PERMISSION_DELETE, PERMISSION_CREATE, PERMISSION_UPDATE
from OperationFrame.ApiFrame.base.exceptions import AccessTokenExpire, BadRequestError, BaseValueError
from OperationFrame.ApiFrame.utils.tools import get_model_pagination
from OperationFrame.config import config
from OperationFrame.config.constant import ENV_DEV
from OperationFrame.lib.depend import paginate_factory
from OperationFrame.utils.models import BaseResponse, BaseResponseList
from OperationFrame.ApiFrame.utils.jwt import create_token, check_permissions

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


@router_user.get('', summary='获取用户列表', response_model=BaseResponseList[List[UserListResponse]],
                 dependencies=[Security(check_permissions, scopes=[f'user_{PERMISSION_INFO}'])])
async def user_list(pagination: dict = paginate_factory(), query: Union[str, int] = None):
    req = get_model_pagination(User, pagination, query)
    data = [
        dict(id=x.id, username=x.username, is_admin=await x.is_admin, is_active=x.is_active,
             department=await x.department_name) for x in await req
    ]

    return BaseResponseList(data=data, total=await User.filter().count())


@router_user.get('/{item_id}', summary='获取用户信息', response_model=BaseResponse[UserInfoResponse],
                 dependencies=[Security(check_permissions, scopes=[f'user_{PERMISSION_INFO}'])])
async def user_info(user: Type[User] = Depends(exists_user)):
    if not isinstance(user, User):
        user = exists_user(user)

    # 查询角色
    roles = [{'id': role.id, 'role_name': role.role_name, 'description': role.description} for role in await user.role]

    # 查询部门
    dep = await user.department
    department = {'id': dep.id, 'department_name': dep.department_name} if dep else {}

    # 查询权限
    permission = []
    for role in await user.role:
        for p in await role.permission:
            permission.append(p.permission_name)

    return BaseResponse(data=dict(id=user.id, is_admin=await user.is_admin, department=department,
                                  username=user.username, is_active=user.is_active, roles=roles, permission=permission))


@router_user.delete('/{item_id}', summary='删除用户', response_model=BaseResponse[UserBase],
                 dependencies=[Security(check_permissions, scopes=[f'user_{PERMISSION_DELETE}'])])
async def user_delete(user: Type[User] = Depends(admin_user)):
    if not isinstance(user, User):
        user = admin_user(user)

    await user.delete()
    return BaseResponse(data=UserBase(username=user.username, is_active=user.is_active))


@router_user.post('', summary='新增用户', response_model=BaseResponse[UserBase],
                 dependencies=[Security(check_permissions, scopes=[f'user_{PERMISSION_CREATE}'])])
async def user_create(user_schema: UserCreateRequest):
    if not isinstance(user_schema, dict):
        user_dict = user_schema.dict(exclude_unset=True)
    else:
        user_dict = user_schema
        if 'username' not in user_dict or 'password' not in user_dict or 'department_id' not in user_dict:
            raise BaseValueError

    roles:        list = user_dict.pop('role_id') if user_dict.get('role_id', None) else []
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

    return BaseResponse(data=UserBase(username=user.username, is_active=user.is_active))


@router_user.put('/{item_id}', summary='修改用户信息', response_model=BaseResponse[UserBase],
                 dependencies=[Security(check_permissions, scopes=[f'user_{PERMISSION_UPDATE}'])])
async def user_update(user_schema: UserUpdateRequest, user: Type[User] = Depends(admin_user)):
    if not isinstance(user, User):
        user = admin_user(user)

    if not isinstance(user_schema, dict):
        user_dict = user_schema.dict(exclude_unset=True)
    else:
        user_dict = user_schema
        if 'username' not in user_dict or 'department_id' not in user_dict:
            raise BaseValueError

    roles:        list = user_dict.pop('role_id') if user_dict.get('role_id', None) else []
    department_id: int = user_dict.pop('department_id')

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

    # 保存信息
    await user.save()

    return BaseResponse(data=UserBase(username=user.username, is_active=user.is_active))


@router_user.get('/menu/{item_id}', summary='用户菜单', response_model=BaseResponse[UserMenuResponse],
                 dependencies=[Security(check_permissions)])
async def user_menu(user: Type[User] = Depends(active_user)):
    if not isinstance(user, User):
        user = active_user(user)

    menus = await user_menu_tree(user)
    return BaseResponse(data=UserMenuResponse(username=user.username, is_active=user.is_active, menus=menus))


@router_user.put('/menu/{item_id}', summary='用户修改菜单', response_model=BaseResponse[UserMenuResponse],
                 dependencies=[Security(check_permissions, scopes=[f'user_{PERMISSION_UPDATE}'])])
async def user_menu_update(user_schema: UserMenuUpdateRequest, user: Type[User] = Depends(active_admin_user)):
    if not isinstance(user, User):
        user = active_admin_user(user)

    if not isinstance(user_schema, dict):
        user_dict = user_schema.dict(exclude_unset=True)
    else:
        user_dict = user_schema

    # 更新用户菜单
    await user.menu.clear()
    menu_objs = [x for x in await Menu.filter(id__in=user_dict['menus']).all()]
    for menu_obj in menu_objs:
        await user.menu.add(menu_obj)

    menus = await user_menu_tree(user)

    return BaseResponse(data=UserMenuResponse(username=user.username, is_active=user.is_active, menus=menus))


# role 模型接口
@router_role.get('', summary='获取角色列表', response_model=BaseResponseList[List[RoleListResponse]],
                 dependencies=[Security(check_permissions, scopes=[f'role_{PERMISSION_INFO}'])])
async def role_list(pagination: dict = paginate_factory(), query: Union[str, int] = None):
    req = get_model_pagination(Role, pagination, query)
    data = [
        dict(id=x.id, role_name=x.role_name, is_admin=x.is_admin, is_active=x.is_active,
             description=x.description) for x in await req
    ]

    return BaseResponseList(data=data, total=await Role.filter().count())


@router_role.get('/{item_id}', summary='获取角色信息', response_model=BaseResponse[RoleInfoResponse],
                 dependencies=[Security(check_permissions, scopes=[f'role_{PERMISSION_INFO}'])])
async def role_info(role: Type[Role] = Depends(exists_role)):
    if not isinstance(role, Role):
        role = exists_role(role)

    permissions = [{'id': menu.id, 'permission_name': menu.permission_name} for menu in await role.permission]
    return BaseResponse(data=dict(id=role.id, is_admin=role.is_admin,  is_active=role.is_active,
                                  role_name=role.role_name, permissions=permissions, description=role.description))


@router_role.delete('/{item_id}', summary='删除角色', response_model=BaseResponse[RoleBase],
                 dependencies=[Security(check_permissions, scopes=[f'role_{PERMISSION_DELETE}'])])
async def role_delete(role: Type[Role] = Depends(admin_role)):
    if not isinstance(role, Role):
        role = admin_role(role)

    await role.delete()
    return BaseResponse(data=RoleBase(role_name=role.role_name, is_active=role.is_active))


@router_role.post('', summary='新增角色', response_model=BaseResponse[RoleBase],
                 dependencies=[Security(check_permissions, scopes=[f'role_{PERMISSION_CREATE}'])])
async def role_create(role_schema: RoleCreateRequest):
    if not isinstance(role_schema, dict):
        role_dict = role_schema.dict(exclude_unset=True)
    else:
        role_dict = role_schema
        if 'permission_id' not in role_dict or 'role_name' not in role_dict \
                or 'description' not in role_dict or 'is_active' not in role_dict:
            raise BaseValueError

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


@router_role.put('/{item_id}', summary='修改角色信息', response_model=BaseResponse[RoleBase],
                 dependencies=[Security(check_permissions, scopes=[f'role_{PERMISSION_UPDATE}'])])
async def role_update(role_schema: RoleUpdateRequest, role: Type[Role] = Depends(admin_role)):
    if not isinstance(role, Role):
        role = admin_role(role)

    if not isinstance(role_schema, dict):
        role_dict = role_schema.dict(exclude_unset=True)
    else:
        role_dict = role_schema
        if 'permission_id' not in role_dict:
            raise BaseValueError

    permission_id: int = role_dict.pop('permission_id')

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
@router_permission.get('', summary='获取权限列表', response_model=BaseResponseList[List[PermissionListResponse]],
                    dependencies=[Security(check_permissions, scopes=[f'permission_{PERMISSION_INFO}'])])
async def permission_list(pagination: dict = paginate_factory(), query: Union[str, int] = None):
    req = get_model_pagination(Permission, pagination, query)
    data = [
        dict(id=x.id, permission_name=x.permission_name, is_active=x.is_active, description=x.description)
        for x in await req
    ]

    return BaseResponseList(data=data, total=await Permission.filter().count())


@router_permission.get('/{item_id}', summary='获取权限信息', response_model=BaseResponse[PermissionInfoResponse],
                    dependencies=[Security(check_permissions, scopes=[f'permission_{PERMISSION_INFO}'])])
async def permission_info(permission: Type[Permission] = Depends(exists_permission)):
    if not isinstance(permission, Permission):
        permission = exists_user(permission)

    roles = [{'id': role.id, 'role_name': role.role_name} for role in await permission.role]
    return BaseResponse(data=dict(id=permission.id, is_active=permission.is_active, roles=roles,
                                  description=permission.description, permission_name=permission.permission_name))


@router_permission.delete('/{item_id}', summary='删除权限', response_model=BaseResponse[PermissionBase],
                    dependencies=[Security(check_permissions, scopes=[f'permission_{PERMISSION_DELETE}'])])
async def permission_delete(permission: Type[Permission] = Depends(exists_permission)):
    if not isinstance(permission, Permission):
        permission = exists_user(permission)

    await permission.delete()
    return BaseResponse(data=PermissionBase(permission_name=permission.permission_name, is_active=permission.is_active))


@router_permission.post('', summary='新增权限', response_model=BaseResponse[PermissionBase],
                    dependencies=[Security(check_permissions, scopes=[f'permission_{PERMISSION_CREATE}'])])
async def permission_create(permission_schema: PermissionCreateRequest):
    if not isinstance(permission_schema, dict):
        permission_dict = permission_schema.dict(exclude_unset=True)
    else:
        permission_dict = permission_schema
        if 'permission_name' not in permission_dict or 'is_active' not in permission_dict \
                or 'description' not in permission_dict:
            raise BaseValueError

    # 检查参数
    if await Permission.filter(permission_name=permission_dict['permission_name']).exists():
        raise BaseValueError(message=f"权限: {permission_dict['permission_name']} 已存在")

    # 创建本表
    permission = await Permission.create(permission_name=permission_dict['permission_name'],
                                         is_active=permission_dict['is_active'],
                                         description=permission_dict['description'])

    return BaseResponse(data=PermissionBase(permission_name=permission.permission_name, is_active=permission.is_active))


@router_permission.put('/{item_id}', summary='修改权限信息', response_model=BaseResponse[PermissionBase],
                    dependencies=[Security(check_permissions, scopes=[f'permission_{PERMISSION_UPDATE}'])])
async def permission_update(permission_schema: PermissionUpdateRequest,
                            permission: Type[Permission] = Depends(exists_permission)):
    if not isinstance(permission, Permission):
        permission = exists_user(permission)

    if not isinstance(permission_schema, dict):
        permission_dict = permission_schema.dict(exclude_unset=True)
    else:
        permission_dict = permission_schema

    # 更新本表
    await permission.update_from_dict(permission_dict)

    # 保存信息
    await permission.save()

    return BaseResponse(data=PermissionBase(permission_name=permission.permission_name, is_active=permission.is_active))
