# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2024/03/12
"""
from fastapi import APIRouter

from . import modelViewSet, action


class HelpInstance(modelViewSet):
    # 路由前缀
    router = APIRouter(prefix='example', tags=['Example'])
    # 注册方法
    methods = ['get']

    def get(self, id: int):
        return {'reload hello': f'world {id}'}

    @action('/help_info/', methods=['GET'])
    def help_info(self, query: str = 'query') -> dict:
        return {'help_info': f'这是一个附加方法 {query}'}
