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


class UserBase(BaseModel):
    username:   str
    is_active: bool


class UserAuthRequest(BaseModel):
    username: str
    password: str


class UserUpdateRequest(UserBase):
    role_id:    List[int] = []
    menu_id:    List[int] = []
    department: int


class UserResponseList(UserBase):
    id:         int
    is_admin:  bool
    department: str


class UserResponseInfo(UserResponseList):
    roles: set = set()
    menus: set = set()


class UserResponse(UserBase):
    is_admin:  bool = False
    permission: set = set()
    token:      str = None
