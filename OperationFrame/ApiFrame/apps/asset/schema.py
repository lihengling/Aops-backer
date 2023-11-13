# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2023/03/21
"""
from typing import Union

from OperationFrame.utils.models import BaseModel


class MenuBase(BaseModel):
    url:       str
    menu_name: str
    parent_id: Union[int, None] = None


class MenuListResponse(MenuBase):
    id:        int
    children:  Union[list, None]


class MenuInfoResponse(MenuListResponse):
    ...


class MenuUpdateRequest(MenuBase):
    ...


class MenuCreateRequest(MenuBase):
    ...


class DepartmentBase(BaseModel):
    department_name: str
    parent_id:       Union[int, None] = None


class DepartmentListResponse(DepartmentBase):
    id:        int
    children:  list = []


class DepartmentInfoResponse(DepartmentBase):
    id:        int
    parent:   list = []


class DepartmentCreateRequest(DepartmentBase):
    ...


class DepartmentUpdateRequest(DepartmentCreateRequest):
    ...
