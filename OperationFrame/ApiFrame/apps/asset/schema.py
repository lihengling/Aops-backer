# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2023/03/21
"""
from typing import Union

from OperationFrame.utils.models import BaseModel


class MenuBase(BaseModel):
    id:         int
    is_show:   bool = True
    menu_name: str
    parent_id: Union[int, None] = None


class MenuListResponse(MenuBase):
    icon:       Union[str, None]
    path:       str
    component:  str
    menu_title: str
    frame_url:  Union[str, None]
    children:   Union[list, None]


class MenuInfoResponse(BaseModel):
    sort:       Union[int, None]
    icon:       Union[str, None]
    path:       str
    is_cache:   bool = False
    component:  str
    menu_title: str
    frame_url:  Union[str, None]
    children:   Union[list, None]


class MenuUpdateRequest(BaseModel):
    sort:       Union[int, None]
    icon:       Union[str, None]
    path:       str
    is_cache:   bool = False
    component:  str
    menu_title: str
    menu_name:  str
    frame_url:  Union[str, None]
    parent_id:  Union[int, None] = None


class MenuCreateRequest(MenuUpdateRequest):
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
