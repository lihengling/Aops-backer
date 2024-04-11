# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2024/03/06
"""
import inspect
from typing import List
from fastapi import APIRouter
from tortoise import Model

from .views import modelView


class modelViewBuilder(type):
    def __new__(mcs, name, bases, attrs):
        mcs = type.__new__(mcs, name, bases, attrs)
        mcs_obj = mcs()

        # 构造元数据
        router:  APIRouter = getattr(mcs, 'router', None)
        methods: List[str] = getattr(mcs, 'methods', [])
        mounted:      bool = getattr(mcs, 'mounted', True)
        querySet:    Model = getattr(mcs, 'querySet', None)
        update_schema:    Model = getattr(mcs, 'update_schema', None)
        create_schema:    Model = getattr(mcs, 'create_schema', None)

        if mounted and router is not None and querySet:
            if 'post' in methods:
                router.add_api_route('/', getattr(mcs_obj, 'post'), methods=['post'])
            if 'get' in methods:
                router.add_api_route('/', getattr(mcs_obj, 'get_list'), methods=['get'])
                router.add_api_route('/{id}/', getattr(mcs_obj, 'get'), methods=['get'])
            if 'put' in methods:
                router.add_api_route('/{id}/', getattr(mcs_obj, 'put'), methods=['put'])
            if 'delete' in methods:
                router.add_api_route('/{id}/', getattr(mcs_obj, 'delete'), methods=['delete'])

            # 自定义api
            funcs = inspect.getmembers(mcs, predicate=inspect.isfunction)
            for name, func in funcs:
                if func.__name__.startswith('API') and func.__dict__:
                    router.add_api_route(func.__dict__.pop('path'), getattr(mcs_obj, name), **func.__dict__)

            fields = mcs.fields if mcs.fields else querySet._meta.db_fields
            mcs.fields = fields.union({'parent_id', 'id'})

        return mcs


class modelViewSet(modelView, metaclass=modelViewBuilder):
    ...


def action(path: str, **kwargs):
    def wrapper(func):
        func.__name__ = f'API-{func.__name__}'
        func.__dict__ = kwargs
        func.__dict__['path'] = path
        return func
    return wrapper
