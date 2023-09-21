# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2023/03/21
"""
from tortoise import fields, Model


class TimestampMixin(Model):
    created_at = fields.DatetimeField(auto_now_add=True, description='创建时间')
    updated_at = fields.DatetimeField(auto_now=True, description='更新时间')

    class Meta:
        abstract = True


class IDModel(TimestampMixin, Model):
    id = fields.IntField(pk=True, description='id')

    class Meta:
        abstract = True


class UUIDModel(TimestampMixin, Model):
    id = fields.UUIDField(pk=True, description='uuid')

    class Meta:
        abstract = True
