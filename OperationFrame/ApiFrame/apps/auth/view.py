# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2023/03/07
"""
from OperationFrame.ApiFrame.apps.auth.models import User, Role
from OperationFrame.ApiFrame.apps.auth.schema import UserResponse, UserRequest, get_user_response
from OperationFrame.ApiFrame.base import router_user, ORJSONResponse, constant
from OperationFrame.ApiFrame.base.exceptions import AccessTokenExpire, BadRequestError
from OperationFrame.utils.models import BaseResponse
from OperationFrame.ApiFrame.utils.jwt import create_token


@router_user.post("/register",
                  summary="用户注册",
                  response_model=BaseResponse[UserResponse])
async def register(data: UserRequest) -> ORJSONResponse:
    if await User.filter(username=data.username).exists():
        raise BadRequestError(message='user %s is exists' % data.username)

    user = await User.create(username=data.username, password=User.get_password(data.password))
    if not await Role.exists():
        role = await Role.create(name='admin', role_name='管理员角色', is_admin=True,
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
