# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2023/03/21
"""
import bcrypt
from async_property import async_property
from tortoise import fields

from OperationFrame.ApiFrame.base.modelMixin import IDModel


class Role(IDModel):
    user: fields.ManyToManyRelation['User']
    role_name = fields.CharField(max_length=30, unique=True, description='角色名称')
    description = fields.TextField(null=True, description='角色描述')
    permission: fields.ManyToManyRelation['Permission'] = \
        fields.ManyToManyField('models.Permission', related_name='role', description='角色权限', on_delete=fields.CASCADE)
    is_active = fields.BooleanField(default=True, description='角色状态(False:禁用,True:启用)')
    is_admin = fields.BooleanField(default=False, description='是否管理员')

    class Meta:
        table = 'roles'
        table_description = '角色表'


class User(IDModel):
    username = fields.CharField(max_length=30, unique=True, description='用户名')
    password = fields.CharField(max_length=128, description='密码')
    role: fields.ManyToManyRelation['Role'] = \
        fields.ManyToManyField('models.Role', related_name='user', description='用户角色', on_delete=fields.CASCADE)
    is_active = fields.BooleanField(default=True, description='用户状态(False:禁用,True:启用)')

    @classmethod
    def get_password(cls, password):
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=10)).decode('utf-8')

    async def set_password(self, password: str):
        self.password = self.get_password(password)
        await self.save(update_fields=['password'])

    def check_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))

    @async_property
    async def is_admin(self) -> bool:
        return await self.role.filter(is_admin=True).exists()

    @async_property
    async def permission(self) -> set:
        user = await User.get(id=self.id).prefetch_related('role__permission')
        permissions = set()
        for role in user.role:
            for permission in role.permission:
                permissions.add(permission.permission_name)
        return permissions

    class AutoModeMeta:
        exclude = ['password']

    class PydanticMeta:
        exclude = ['password']

    class Meta:
        table = 'users'
        table_description = '用户表'
        query_fields = ['username', 'created_at', 'updated_at']


class Permission(IDModel):
    role: fields.ManyToManyRelation['Role']
    permission_name = fields.CharField(max_length=30, description='权限名称')
    description = fields.TextField(null=True, description='权限描述')
    parent_id = fields.IntField(default=0, description='父id')
    is_active = fields.BooleanField(default=True, description='权限状态(False:禁用,True:启用)')

    class Meta:
        table = 'permissions'
        table_description = '权限表'
