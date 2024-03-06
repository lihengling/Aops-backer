# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2023/03/21
"""
from datetime import datetime
from typing import List

from fastapi import Query

from OperationFrame.ApiFrame.apps.rbac.models import User, Role, Permission
from OperationFrame.ApiFrame.base import ORJSONResponse
from OperationFrame.utils.models import BaseModel, BaseResponse


# user 模型 schema
class UserBase(BaseModel):
    username:   str
    is_active: bool = True


class UserAuthRequest(BaseModel):
    username: str
    password: str


class UserAuthResponse(UserBase):
    id:         int
    is_admin:  bool = False
    permission: set = set()
    token:      str = None


class UserListResponse(UserBase):
    id:            int
    is_admin:      bool
    department: str
    created_at:    datetime
    role:          list = []
    menu:          list = []


class UserUpdateRequest(BaseModel):
    username:      str = Query(..., description='用户名', max_length=50, min_length=1)
    is_active:    bool = Query(True, description='是否启用')
    role_id: List[int] = Query([], description='角色id')
    menu_id: List[int] = Query([], description='菜单id')
    department_id: int = Query(..., description='部门id')


class UserCreateRequest(UserUpdateRequest, UserAuthRequest):
    ...


class UserMenuResponse(UserBase):
    menus: List[dict] = []


async def get_user_response(user: User, token: str = None) -> ORJSONResponse:
    return ORJSONResponse(
        BaseResponse(data=UserAuthResponse(
            id=user.id,
            username=user.username,
            is_active=user.is_active,
            is_admin=await user.is_admin,
            permission=await user.permission,
            token=token,
        )))


# permission 模型 schema
class PermissionBase(BaseModel):
    permission_name: str
    is_active:       bool


class PermissionListResponse(BaseModel):
    id:              int
    description:     str
    permission_name: str
    is_active:       bool


class PermissionCreateRequest(BaseModel):
    permission_name: str = Query(..., description='权限名称', max_length=50, min_length=1)
    is_active:      bool = Query(True, description='是否启用')
    description:     str = Query('', description='权限描述', max_length=255)


class PermissionUpdateRequest(PermissionCreateRequest):
    id:              int = Query(..., description='主键id', gt=0)


def get_permission_response(obj: Permission) -> BaseResponse:
    return BaseResponse(data=PermissionBase(is_active=obj.is_active, permission_name=obj.permission_name))


# role 模型 schema
class RoleBase(BaseModel):
    name:        str
    role_name:   str
    is_active:   bool


class RoleListResponse(BaseModel):
    id:          int
    name:        str
    description: str
    role_name:   str
    is_admin:    bool
    is_active:   bool
    permissions: List[PermissionListResponse] = []


class RoleCreateRequest(BaseModel):
    name:           str = Query(..., description='角色标识', max_length=50, min_length=1)
    role_name:      str = Query(..., description='角色名称', max_length=50, min_length=1)
    is_active:     bool = Query(True, description='是否启用')
    permission_id: list = Query([], description='权限id列表')
    description:    str = Query('', description='角色描述', max_length=255)


class RoleUpdateRequest(RoleCreateRequest):
    id:             int = Query(..., description='主键id', gt=0)


def get_role_response(obj: Role) -> BaseResponse:
    return BaseResponse(data=RoleBase(is_active=obj.is_active, role_name=obj.role_name, name=obj.name))


