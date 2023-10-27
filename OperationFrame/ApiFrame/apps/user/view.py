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

from OperationFrame.ApiFrame.apps.user.models import User, Role
from OperationFrame.ApiFrame.apps.user.schema import UserResponse, UserRequest, get_user_response, UserResponseList, \
    UserResponseInfo
from OperationFrame.ApiFrame.base import router_user, ORJSONResponse, constant
from OperationFrame.ApiFrame.base.exceptions import AccessTokenExpire, BadRequestError, NotFindError
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
async def register(data: UserRequest) -> ORJSONResponse:
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
async def login(data: UserRequest) -> ORJSONResponse:
    user = await User.filter(username=data.username).first()
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

    data = []
    for res in await req:
        data.append(dict(username=res.username, is_admin=await res.is_admin, is_active=res.is_active,
                         department=await res.department_name))

    return BaseResponseList(data=data, total=await User.filter().count())


@router_user.get('/{item_id}', summary='获取用户详细信息', response_model=BaseResponse[UserResponseInfo])
async def user_info(item_id: int):
    res = await User.filter(id=item_id).first()
    if res:
        return BaseResponse(data=dict(is_admin=await res.is_admin, department=await res.department_name,
                            username=res.username, is_active=res.is_active))
    else:
        raise NotFindError


async def user_create():
    pass


async def user_delete():
    pass


async def user_update():
    pass

