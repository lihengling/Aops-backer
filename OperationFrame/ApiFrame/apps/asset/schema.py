# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2023/03/21
"""
from datetime import datetime
from typing import Union

from fastapi import Query
from pydantic import validator

from OperationFrame.ApiFrame.apps.asset.models import Menu, Department
from OperationFrame.ApiFrame.base.exceptions import BaseValueError
from OperationFrame.utils.models import BaseModel, BaseResponse


class MenuBase(BaseModel):
    id:         int
    menu_name:  str
    is_active:  bool


class MenuListResponse(BaseModel):
    id:         int
    menu_name:  str
    menu_title: str
    path:       str
    component:  str
    is_active:  bool
    is_show:    bool
    is_cache:   bool
    is_menu:    bool
    redirect:   Union[str, None]
    parent_id:  Union[int, None]
    icon:       Union[str, None]
    frame_url:  Union[str, None]
    children:   Union[list, None]


class MenuCreateRequest(BaseModel):
    menu_name:  str = Query(..., description='名称', max_length=30, min_length=1)
    menu_title: str = Query(..., description='标题', max_length=30, min_length=1)
    path:       str = Query(..., description='路径名', min_length=1)
    component:  str = Query(..., description='组件', max_length=100)
    redirect:   str = Query(None, description='重定向路由', max_length=100)
    icon:       str = Query(None, description='图标', max_length=200)
    frame_url:  str = Query(None, description='外链接地址')
    parent_id:  int = Query(None, description='父id', gt=0)
    sort:       int = Query(None, description='排序')
    is_cache:  bool = Query(False, description='是否缓存')
    is_active: bool = Query(True, description='是否启用')
    is_show:   bool = Query(True, description='是否展示')


class MenuUpdateRequest(MenuCreateRequest):
    id:         int = Query(..., description='主键id', gt=0)


def get_menu_response(obj: Menu) -> BaseResponse:
    return BaseResponse(data=MenuBase(id=obj.id, is_active=obj.is_active, menu_name=obj.menu_name))


class DepartmentBase(BaseModel):
    id:              int
    is_active:       bool
    department_name: str


class DepartmentListResponse(BaseModel):
    id:              int
    is_active:       bool
    created_at:      datetime
    children:        list = []
    description:     str
    department_name: str


class DepartmentCreateRequest(BaseModel):
    department_name: str = Query(..., description='部门名称', max_length=50, min_length=1)
    is_active:      bool = Query(True, description='是否启用')
    parent_id:       int = Query(None, description='父id', gt=0)
    description:     str = Query('', description='部门描述', max_length=255)


class DepartmentUpdateRequest(DepartmentCreateRequest):
    id:              int = Query(..., description='主键id', gt=0)

    @validator('id')
    def id_not_equal_parent_id(cls, v, values):
        if 'parent_id' in values and v == values['parent_id']:
            raise BaseValueError(message=f"更新失败 | 父级id 不能为自身 id")
        return v


def get_department_response(obj: Department) -> BaseResponse:
    return BaseResponse(data=DepartmentBase(id=obj.id, is_active=obj.is_active, department_name=obj.department_name))
