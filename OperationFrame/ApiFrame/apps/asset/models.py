# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2023/03/21
"""
from tortoise import fields

from OperationFrame.ApiFrame.apps.rbac.models import User
from OperationFrame.ApiFrame.base.modelMixin import IDModel


class Department(IDModel):
    department_name = fields.CharField(max_length=30, description='部门名称')
    parent = fields.ForeignKeyField('models.Department', related_name='children', description='父部门关系外键', null=True)

    class Meta:
        table = 'department'
        table_description = '部门表'


class Menu(IDModel):
    user: fields.ManyToManyRelation['User']
    menu_name = fields.CharField(max_length=30, description='菜单名称')
    url = fields.CharField(max_length=255, description='菜单链接')
    parent = fields.ForeignKeyField('models.Menu', related_name='children', description='父菜单关系外键', null=True)

    class Meta:
        table = 'menu'
        table_description = '菜单表'
