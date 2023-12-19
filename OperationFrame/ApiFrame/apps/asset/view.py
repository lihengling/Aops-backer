# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2023/03/07
"""
from typing import List

from fastapi import Depends, Security, Query

from OperationFrame.ApiFrame.apps.asset.models import Menu, Department
from OperationFrame.ApiFrame.apps.asset.schema import MenuListResponse, MenuBase, MenuCreateRequest, \
    MenuUpdateRequest, DepartmentListResponse, DepartmentBase, DepartmentCreateRequest, \
    DepartmentUpdateRequest, get_menu_response, get_department_response
from OperationFrame.ApiFrame.apps.asset.utils import full_department_tree
from OperationFrame.ApiFrame.apps.rbac.utils import full_menu_tree
from OperationFrame.ApiFrame.base import router_menu,  router_department, PERMISSION_UPDATE, \
    PERMISSION_INFO, PERMISSION_DELETE, PERMISSION_CREATE
from OperationFrame.ApiFrame.utils.curd import CurdGenerator
from OperationFrame.ApiFrame.utils.jwt import check_permissions
from OperationFrame.lib.depend import PageQuery
from OperationFrame.utils.models import BaseResponseList, BaseResponse

# 初始化 curd
curd_menu:       CurdGenerator = CurdGenerator(Menu, MenuUpdateRequest, MenuCreateRequest)
curd_department: CurdGenerator = CurdGenerator(Department, DepartmentUpdateRequest, DepartmentCreateRequest)


# Menu 模型接口
@router_menu.get('/list/', summary='获取菜单列表', response_model=BaseResponseList[List[MenuListResponse]],
                dependencies=[Security(check_permissions, scopes=[f'menu_{PERMISSION_INFO}'])])
async def menu_list(pq: PageQuery = Depends(PageQuery)):
    return BaseResponseList(data=await full_menu_tree(pq), total=await Menu.filter().count())


@router_menu.delete('/', summary='删除菜单', response_model=BaseResponse[MenuBase],
                dependencies=[Security(check_permissions, scopes=[f'menu_{PERMISSION_DELETE}'])])
async def menu_delete(schema: int = Query(..., description='主键id', gt=0, alias='id')):
    return get_menu_response(await curd_menu.delete_item(schema))


@router_menu.post('/', summary='新增菜单', response_model=BaseResponse[MenuBase],
                dependencies=[Security(check_permissions, scopes=[f'menu_{PERMISSION_CREATE}'])])
async def menu_create(schema: MenuCreateRequest):
    return get_menu_response(await curd_menu.create_item(schema))


@router_menu.put('/', summary='修改菜单信息', response_model=BaseResponse[MenuBase],
                dependencies=[Security(check_permissions, scopes=[f'menu_{PERMISSION_UPDATE}'])])
async def menu_update(schema: MenuUpdateRequest):
    return get_menu_response(await curd_menu.update_item(schema))


# Department 模型接口
@router_department.get('/list/', summary='获取部门列表', response_model=BaseResponseList[List[DepartmentListResponse]],
                dependencies=[Security(check_permissions, scopes=[f'department_{PERMISSION_INFO}'])])
async def department_list(pq: PageQuery = Depends(PageQuery)):
    return BaseResponseList(data=await full_department_tree(pq), total=await Department.filter().count())


@router_department.delete('/', summary='删除部门', response_model=BaseResponse[DepartmentBase],
                dependencies=[Security(check_permissions, scopes=[f'department_{PERMISSION_DELETE}'])])
async def department_delete(schema: int = Query(..., description='主键id', gt=0, alias='id')):
    return get_department_response(await curd_department.delete_item(schema))


@router_department.post('/', summary='新增部门', response_model=BaseResponse[DepartmentBase],
                dependencies=[Security(check_permissions, scopes=[f'department_{PERMISSION_CREATE}'])])
async def department_create(schema: DepartmentCreateRequest):
    return get_department_response(await curd_department.create_item(schema))


@router_department.put('/', summary='修改部门信息', response_model=BaseResponse[DepartmentBase],
                dependencies=[Security(check_permissions, scopes=[f'department_{PERMISSION_UPDATE}'])])
async def department_update(schema: DepartmentUpdateRequest):
    return get_department_response(await curd_department.update_item(schema))
