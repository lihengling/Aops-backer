# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2023/03/21
"""
from tortoise import fields

from OperationFrame.ApiFrame.apps.rbac.models import User
from OperationFrame.ApiFrame.base.modelMixin import IDModel


class Department(IDModel):
    department_name = fields.CharField(max_length=30, description='部门名称', unique=True)
    parent = fields.ForeignKeyField('models.Department', related_name='children', description='父部门关系外键', null=True)
    is_active = fields.BooleanField(default=True, description='部门是否启用')
    description = fields.CharField(max_length=255, null=True, description='部门描述')
    # parent_id: fields.ForeignKeyField

    class Meta:
        table = 'department'
        table_description = '部门表'


class Menu(IDModel):
    user: fields.ManyToManyRelation['User']
    menu_title = fields.CharField(max_length=30, description='菜单标题', unique=True)
    menu_name = fields.CharField(max_length=30, description='菜单名称', unique=True)
    icon = fields.CharField(max_length=200, null=True, description='菜单图标')
    path = fields.CharField(max_length=255, null=True, description='菜单路径名', unique=True)
    redirect = fields.CharField(max_length=255, null=True, description='菜单重定向')
    is_show = fields.BooleanField(default=True, description='菜单是否显示')
    is_active = fields.BooleanField(default=True, description='菜单是否启用')
    is_cache = fields.BooleanField(default=False, description='菜单是否缓存')
    frame_url = fields.CharField(max_length=255, null=True, description='外链url地址, 如不为空则为外链菜单')
    sort = fields.IntField(null=True, description='排序, 菜单按数字大小排序返回')
    component = fields.CharField(max_length=100, null=True, description='组件名称')
    parent = fields.ForeignKeyField('models.Menu', related_name='children', description='父菜单关系外键', null=True)
    # parent_id: fields.ForeignKeyField

    @property
    def is_menu(self) -> bool:
        return '#' not in self.component

    class Meta:
        table = 'menu'
        table_description = '菜单表'
