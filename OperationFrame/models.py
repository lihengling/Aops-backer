# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2022/07/27
"""
from tortoise import fields
from tortoise.models import Model


class Game(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)

    class Meta:
        table = 'game'
        query_fields = ['name']
