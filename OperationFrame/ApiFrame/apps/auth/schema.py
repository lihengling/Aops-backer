# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2023/03/21
"""
from OperationFrame.ApiFrame.apps.auth.models import User
from OperationFrame.ApiFrame.base import ORJSONResponse
from OperationFrame.utils.models import BaseModel, BaseResponse


class UserRequest(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    username: str
    is_admin: bool = False
    permission: set = set()
    token: str = None


async def get_user_response(user: User, token: str = None) -> ORJSONResponse:
    return ORJSONResponse(
        BaseResponse(data=UserResponse(
            username=user.username,
            is_admin=await user.is_admin,
            permission=await user.permission,
            token=token,
        )))
