# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2023/03/07
"""
from typing import List, Union, Type

from fastapi import Depends

from OperationFrame.ApiFrame.apps.asset.depends import exists_menu, exists_department
from OperationFrame.ApiFrame.apps.asset.models import Menu, Department
from OperationFrame.ApiFrame.apps.asset.schema import MenuListResponse, MenuInfoResponse, MenuBase, MenuCreateRequest, \
    MenuUpdateRequest, DepartmentListResponse, DepartmentInfoResponse, DepartmentBase, DepartmentCreateRequest, \
    DepartmentUpdateRequest
from OperationFrame.ApiFrame.apps.asset.utils import full_department_tree, id_department_tree
from OperationFrame.ApiFrame.apps.rbac.utils import full_menu_tree, id_menu_tree
from OperationFrame.ApiFrame.base import router_menu, NotFindError, router_department
from OperationFrame.ApiFrame.base.exceptions import BaseValueError
from OperationFrame.lib.depend import paginate_factory
from OperationFrame.utils.models import BaseResponseList, BaseResponse


# Menu 模型接口
@router_menu.get('', summary='获取菜单列表', response_model=BaseResponseList[List[MenuListResponse]])
async def menu_list(pagination: dict = paginate_factory(), query: Union[str, int] = None):
    data = await full_menu_tree(pagination, query)
    return BaseResponseList(data=data, total=await Menu.filter().count())


@router_menu.get('/{item_id}', summary='获取菜单信息', response_model=BaseResponse[List[MenuInfoResponse]])
async def menu_info(item_id: int):
    obj = await Menu.get_or_none(id=item_id)
    if not obj:
        raise NotFindError

    menus = await id_menu_tree(item_id)
    return BaseResponse(data=menus)


@router_menu.delete('/{item_id}', summary='删除权限', response_model=BaseResponse[MenuBase])
async def menu_delete(menu: Type[Menu] = Depends(exists_menu)):
    if not isinstance(menu, Menu):
        menu = exists_menu(menu)

    await menu.delete()
    return BaseResponse(data=MenuBase(id=menu.id, url=menu.url, menu_name=menu.menu_name, parent_id=menu.parent_id))


@router_menu.post('', summary='新增菜单', response_model=BaseResponse[MenuBase])
async def menu_create(menu_schema: MenuCreateRequest):
    if not isinstance(menu_schema, dict):
        menu_dict = menu_schema.dict()
    else:
        menu_dict = menu_schema
        if 'menu_name' not in menu_dict or 'url' not in menu_dict:
            raise BaseValueError

    # 检查参数
    if await Menu.filter(menu_name=menu_dict['menu_name']).exists():
        raise BaseValueError(message=f"菜单: {menu_dict['menu_name']} 已存在")

    if menu_dict['parent_id']:
        if not await Menu.filter(id=menu_dict['parent_id']).exists():
            raise BaseValueError(message=f"父菜单id: {menu_dict['parent_id']} 不存在")

    # 创建本表
    menu = await Menu.create(menu_name=menu_dict['menu_name'], url=menu_dict['url'],
                             parent_id=menu_dict['parent_id'])

    return BaseResponse(data=MenuBase(id=menu.id, menu_name=menu.menu_name, parent_id=menu.parent_id,
                                      url=menu.url))


@router_menu.put('/{item_id}', summary='修改菜单信息', response_model=BaseResponse[MenuBase])
async def menu_update(menu_schema: MenuUpdateRequest, menu: Type[Menu] = Depends(exists_menu)):
    if not isinstance(menu, Menu):
        menu = exists_menu(menu)

    if not isinstance(menu_schema, dict):
        menu_dict = menu_schema.dict(exclude_unset=True)
    else:
        menu_dict = menu_schema

    # 更新本表
    await menu.update_from_dict(menu_dict)

    # 保存信息
    await menu.save()

    return BaseResponse(data=MenuBase(id=menu.id, menu_name=menu.menu_name, parent_id=menu.parent_id,
                                      url=menu.url))


# Department 模型接口
@router_department.get('', summary='获取部门列表', response_model=BaseResponseList[List[DepartmentListResponse]])
async def department_list(pagination: dict = paginate_factory(), query: Union[str, int] = None):
    data = await full_department_tree(pagination, query)
    return BaseResponseList(data=data, total=await Department.filter().count())


@router_department.get('/{item_id}', summary='获取部门信息', response_model=BaseResponse[DepartmentInfoResponse])
async def department_info(item_id: int):
    obj = await Department.get_or_none(id=item_id)
    if not obj:
        raise NotFindError

    department = await id_department_tree(item_id)
    return BaseResponse(data=DepartmentInfoResponse(id=obj.id, department_name=obj.department_name,
                                                    parent_id=obj.parent_id, parent=department))


@router_department.delete('/{item_id}', summary='删除部门', response_model=BaseResponse[DepartmentBase])
async def department_delete(department: Type[Department] = Depends(exists_department)):
    if not isinstance(department, Department):
        department = exists_department(department)

    await department.delete()
    return BaseResponse(data=DepartmentBase(department_name=department.department_name, parent_id=department.parent_id))


@router_department.post('', summary='新增部门', response_model=BaseResponse[DepartmentBase])
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


@router_department.put('/{item_id}', summary='修改部门信息', response_model=BaseResponse[DepartmentBase])
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
