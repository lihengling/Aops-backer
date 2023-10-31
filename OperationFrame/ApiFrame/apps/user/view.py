# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2023/03/07
"""
from typing import Union, cast, List
from functools import reduce
from operator import or_
from fastapi import Depends
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

from OperationFrame.ApiFrame.apps.user.models import User, Role, Menu, Department
from OperationFrame.ApiFrame.apps.user.schema import UserResponse, UserAuthRequest, get_user_response, UserResponseList, \
    UserResponseInfo, UserUpdateRequest
from OperationFrame.ApiFrame.base import router_user, ORJSONResponse, constant
from OperationFrame.ApiFrame.base.exceptions import AccessTokenExpire, BadRequestError, NotFindError, ForbiddenError, \
    BaseValueError
from OperationFrame.ApiFrame.utils.cbv.core import get_cbv_exp
from OperationFrame.config import config
from OperationFrame.config.constant import ENV_DEV
from OperationFrame.lib.depend import paginate_factory
from OperationFrame.utils.models import BaseResponse, BaseResponseList
from OperationFrame.ApiFrame.utils.jwt import create_token

# User 模型权限前缀
model_name = User.__name__.lower()


if config.ENV == ENV_DEV:
    @router_user.post("/token", summary="docs 获取 token，仅用于开发环境测试")
    async def login_oauth(data: OAuth2PasswordRequestForm = Depends()):
        user = await User.filter(username=data.username).first()
        jwt_token = create_token(data={
            "username": user.username,
            "password": user.get_password(data.password)
        })

        return {'access_token': jwt_token, 'token_type': constant.JWT_TOKEN_TYPE}


@router_user.post("/register",
                  summary="用户注册",
                  response_model=BaseResponse[UserResponse])
async def register(data: UserAuthRequest) -> ORJSONResponse:
    if await User.filter(username=data.username).exists():
        raise BadRequestError(message=f'user {data.username} is exists')

    user = await User.create(username=data.username, password=User.get_password(data.password))
    if not await Role.exists():
        role = await Role.create(name='admin', role_name='管理员', is_admin=True,
                                 description='拥有所有权限')
        await user.role.add(role)
    return await get_user_response(user)


@router_user.post("/login",
                  summary="用户登录",
                  response_model=BaseResponse[UserResponse])
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


@router_user.get('', summary='获取用户列表', response_model=BaseResponseList[List[UserResponseList]])
async def user_list(pagination: dict = paginate_factory(), query: Union[str, int] = None):
    skip, limit = pagination.get("skip", 0), pagination.get("limit", None)
    query_model = User.filter(reduce(or_, get_cbv_exp(User, query))) if query is not None else User
    req = query_model.all().offset(cast(int, skip))
    if limit:
        req = req.limit(limit)

    data = [dict(id=x.id, username=x.username, is_admin=await x.is_admin, is_active=x.is_active,
                 department=await x.department_name) for x in await req]

    return BaseResponseList(data=data, total=await User.filter().count())


@router_user.get('/{item_id}', summary='获取用户信息', response_model=BaseResponse[UserResponseInfo])
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


@router_user.delete('/{item_id}', summary='删除用户', response_model=BaseResponse[UserResponse])
async def user_delete(item_id: int):
    user = await User.get_or_none(id=item_id)
    if not user:
        raise NotFindError

    if await user.is_admin:
        raise ForbiddenError(message='管理员用户不可删除')
    else:
        await user.delete()
        return BaseResponse(data=UserResponse(username=user.username))


@router_user.put('/{item_id}', summary='修改用户信息')
# @router_user.put('/{item_id}', summary='修改用户信息', response_model=BaseResponse[UserResponse])
async def user_update(item_id: int, user_schema: Union[UserUpdateRequest, dict]):
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

    return BaseResponse(data=[])
