# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2023/03/21
"""
from typing import List

from OperationFrame.ApiFrame.apps.user.models import User
from OperationFrame.ApiFrame.base import ORJSONResponse
from OperationFrame.utils.models import BaseModel, BaseResponse


async def get_user_response(user: User, token: str = None) -> ORJSONResponse:
    return ORJSONResponse(
        BaseResponse(data=UserResponse(
            username=user.username,
            is_active=user.is_active,
            is_admin=await user.is_admin,
            permission=await user.permission,
            token=token,
        )))


# 响应: 用户基础字段
class UserBase(BaseModel):
    username:   str
    is_active: bool


# 请求: 用户登录注册请求
class UserAuthRequest(BaseModel):
    username: str
    password: str


# 请求: 用户修改信息
class UserUpdateRequest(UserBase):
    role_id:       List[int] = []
    menu_id:       List[int] = []
    department_id: int


# 响应: 用户列表
class UserResponseList(UserBase):
    id:         int
    is_admin:  bool
    department: str


# 响应: 用户信息
class UserResponseInfo(UserResponseList):
    roles: List[dict] = []
    menus: List[dict] = []
    department:  dict


# 响应: 用户token信息
class UserResponse(UserBase):
    is_admin:  bool = False
    permission: set = set()
    token:      str = None
