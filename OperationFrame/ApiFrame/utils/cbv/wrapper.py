# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2023/03/21
"""

from enum import Enum
from typing import *
from typing import Callable, Any, Coroutine

from fastapi import params
from fastapi.datastructures import Default
from fastapi.encoders import SetIntStr, DictIntStrAny
from fastapi.routing import APIRoute
from fastapi.utils import generate_unique_id
from starlette.responses import JSONResponse, Response
from starlette.routing import BaseRoute

from .const import *


def api_route(
        path: str = None,
        response_model: Optional[Type[Any]] = None,
        status_code: Optional[int] = None,
        tags: Optional[List[Union[str, Enum]]] = None,
        dependencies: Optional[Sequence[params.Depends]] = None,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        response_description: str = "Successful Response",
        responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
        deprecated: Optional[bool] = None,
        operation_id: Optional[str] = None,
        response_model_include: Optional[Union[SetIntStr, DictIntStrAny]] = None,
        response_model_exclude: Optional[Union[SetIntStr, DictIntStrAny]] = None,
        response_model_by_alias: bool = True,
        response_model_exclude_unset: bool = False,
        response_model_exclude_defaults: bool = False,
        response_model_exclude_none: bool = False,
        include_in_schema: bool = True,
        response_class: Type[Response] = Default(JSONResponse),
        name: Optional[str] = None,
        callbacks: Optional[List[BaseRoute]] = None,
        openapi_extra: Optional[Dict[str, Any]] = None,
        generate_unique_id_function: Callable[[APIRoute], str] = Default(generate_unique_id),
) -> Callable[[Coroutine], Coroutine[Any, Any, Coroutine]]:
    def decorator(coroutine_function: Coroutine):
        # 当不存在返回值类型声明时自动注入返回值类型
        _response_model = response_model
        if not response_model and 'return' in coroutine_function.__annotations__:
            _response_model = coroutine_function.__annotations__['return']
        _path = path
        setattr(coroutine_function, CBV_API_ROUTE, {
            'path': _path,
            'response_model': _response_model,
            'status_code': status_code,
            'tags': tags,
            'dependencies': dependencies,
            'summary': summary,
            'description': description,
            'response_description': response_description,
            'responses': responses,
            'deprecated': deprecated,
            'operation_id': operation_id,
            'response_model_include': response_model_include,
            'response_model_exclude': response_model_exclude,
            'response_model_by_alias': response_model_by_alias,
            'response_model_exclude_unset': response_model_exclude_unset,
            'response_model_exclude_defaults': response_model_exclude_defaults,
            'response_model_exclude_none': response_model_exclude_none,
            'include_in_schema': include_in_schema,
            'response_class': response_class,
            'name': name,
            'callbacks': callbacks,
            'openapi_extra': openapi_extra,
            'generate_unique_id_function': generate_unique_id_function,
        })
        return coroutine_function

    return decorator


def set_meta(action, value=None, **kwargs):
    def wrapper(coroutine_function: Coroutine):
        setattr(coroutine_function, action, value or kwargs)
        return coroutine_function

    return wrapper
