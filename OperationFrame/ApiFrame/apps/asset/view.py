# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2023/03/07
"""
from typing import List, Union, Type

from fastapi import Depends, Security, Query

from OperationFrame.ApiFrame.apps.asset.depends import exists_department
from OperationFrame.ApiFrame.apps.asset.models import Menu, Department
from OperationFrame.ApiFrame.apps.asset.schema import MenuListResponse, MenuBase, MenuCreateRequest, \
    MenuUpdateRequest, DepartmentListResponse, DepartmentInfoResponse, DepartmentBase, DepartmentCreateRequest, \
    DepartmentUpdateRequest, get_menu_response
from OperationFrame.ApiFrame.apps.asset.utils import full_department_tree, id_department_tree
from OperationFrame.ApiFrame.apps.rbac.utils import full_menu_tree
from OperationFrame.ApiFrame.base import router_menu, NotFindError, router_department, PERMISSION_UPDATE, \
    PERMISSION_INFO, PERMISSION_DELETE, PERMISSION_CREATE
from OperationFrame.ApiFrame.base.exceptions import BaseValueError
from OperationFrame.ApiFrame.utils.curd import CurdGenerator
from OperationFrame.ApiFrame.utils.jwt import check_permissions
from OperationFrame.lib.depend import paginate_factory
from OperationFrame.utils.models import BaseResponseList, BaseResponse

# 初始化 curd
curd_menu = CurdGenerator(Menu, MenuUpdateRequest, MenuCreateRequest)


# Menu 模型接口
@router_menu.get('/list/', summary='获取菜单列表', response_model=BaseResponseList[List[MenuListResponse]],
                dependencies=[Security(check_permissions, scopes=[f'menu_{PERMISSION_INFO}'])])
async def menu_list(pagination: dict = paginate_factory(), query: Union[str, int] = None):
    data = await full_menu_tree(pagination, query)
    return BaseResponseList(data=data, total=await Menu.filter().count())


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
async def department_list(pagination: dict = paginate_factory(), query: Union[str, int] = None):
    data = await full_department_tree(pagination, query)
    return BaseResponseList(data=data, total=await Department.filter().count())


@router_department.get('/info/', summary='获取部门信息', response_model=BaseResponse[DepartmentInfoResponse],
                dependencies=[Security(check_permissions, scopes=[f'department_{PERMISSION_INFO}'])])
async def department_info(item_id: int):
    obj = await Department.get_or_none(id=item_id)
    if not obj:
        raise NotFindError

    department = await id_department_tree(item_id)
    return BaseResponse(data=DepartmentInfoResponse(id=obj.id, department_name=obj.department_name,
                                                    parent_id=obj.parent_id, parent=department))


@router_department.delete('/', summary='删除部门', response_model=BaseResponse[DepartmentBase],
                dependencies=[Security(check_permissions, scopes=[f'department_{PERMISSION_DELETE}'])])
async def department_delete(department: Type[Department] = Depends(exists_department)):
    if not isinstance(department, Department):
        department = exists_department(department)

    await department.delete()
    return BaseResponse(data=DepartmentBase(department_name=department.department_name, parent_id=department.parent_id))


@router_department.post('/', summary='新增部门', response_model=BaseResponse[DepartmentBase],
                dependencies=[Security(check_permissions, scopes=[f'department_{PERMISSION_CREATE}'])])
async def department_create(department_schema: DepartmentCreateRequest):
    if not isinstance(department_schema, dict):
        department_dict = department_schema.dict()
    else:
        department_dict = department_schema
        if 'department_name' not in department_dict:
            raise BaseValueError

    parent_id = department_dict.get('parent_id', None)

    # 检查参数
    if await Department.filter(department_name=department_dict['department_name']).exists():
        raise BaseValueError(message=f"部门: {department_dict['department_name']} 已存在")

    if parent_id:
        if not await Department.filter(id=parent_id).exists():
            raise BaseValueError(message=f"父部门id: {parent_id} 不存在")

    # 创建本表
    department = await Department.create(department_name=department_dict['department_name'],
                                         parent_id=parent_id if parent_id and isinstance(parent_id, int) else None)

    return BaseResponse(data=DepartmentBase(department_name=department.department_name, parent_id=department.parent_id))


@router_department.put('/', summary='修改部门信息', response_model=BaseResponse[DepartmentBase],
                dependencies=[Security(check_permissions, scopes=[f'department_{PERMISSION_UPDATE}'])])
async def department_update(department_schema: DepartmentUpdateRequest,
                            department: Type[Department] = Depends(exists_department)):
    if not isinstance(department, Department):
        department = exists_department(department)

    if not isinstance(department_schema, dict):
        department_dict = department_schema.dict(exclude_unset=True)
    else:
        department_dict = department_schema

    # 更新本表
    await department.update_from_dict(department_dict)

    # 保存信息
    await department.save()

    return BaseResponse(data=DepartmentBase(department_name=department.department_name, parent_id=department.parent_id))
