# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2023/03/21
"""
from typing import List

from OperationFrame.ApiFrame.apps.rbac.models import User
from OperationFrame.ApiFrame.base import ORJSONResponse
from OperationFrame.utils.models import BaseModel, BaseResponse


# user 模型 schema
class UserBase(BaseModel):
    username:   str
    is_active: bool


class UserAuthRequest(BaseModel):
    username: str
    password: str


class UserAuthResponse(UserBase):
    is_admin:  bool = False
    permission: set = set()
    token:      str = None


async def get_user_response(user: User, token: str = None) -> ORJSONResponse:
    return ORJSONResponse(
        BaseResponse(data=UserAuthResponse(
            username=user.username,
            is_active=user.is_active,
            is_admin=await user.is_admin,
            permission=await user.permission,
            token=token,
        )))


class UserListResponse(UserBase):
    id:         int
    is_admin:  bool
    department: str


class UserInfoResponse(UserListResponse):
    roles: List[dict] = []
    menus: List[dict] = []
    department:  dict


class UserUpdateRequest(UserBase):
    role_id:       List[int] = []
    menu_id:       List[int] = []
    department_id: int


class UserCreateRequest(UserUpdateRequest, UserAuthRequest):
    ...


# role 模型 schema
class RoleBase(BaseModel):
    role_name: str
    is_active: bool


class RoleListResponse(RoleBase):
    id:          int
    is_admin:   bool
    description: str


class RoleInfoResponse(RoleListResponse):
    permissions: List[dict] = []


class RoleUpdateRequest(RoleBase):
    permission_id: List[int] = []
    description:   str


class RoleCreateRequest(RoleUpdateRequest):
    ...


# permission 模型 schema
class PermissionBase(BaseModel):
    permission_name: str
    is_active:      bool


class PermissionListResponse(PermissionBase):
    id:          int
    description: str


class PermissionInfoResponse(PermissionListResponse):
    roles:       List[dict] = []


class PermissionUpdateRequest(PermissionBase):
    description: str


class PermissionCreateRequest(PermissionUpdateRequest):
    ...
