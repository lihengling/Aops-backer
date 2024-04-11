# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2023/03/21
"""

import typing

from pydantic import BaseModel
from pydantic.generics import GenericModel

from .const import LIMIT, OFFSET

OBJ_DATA = typing.TypeVar('OBJ_DATA')
LIST_DATA = typing.TypeVar('LIST_DATA')


class BaseObjectResponse(GenericModel, typing.Generic[OBJ_DATA]):
    code: int = 200
    message: str = 'ok'
    data: OBJ_DATA = None


class MetaResponse(BaseModel):
    limit: int = LIMIT
    offset: int = OFFSET
    total_count: int = 0


class ListResponseData(GenericModel, typing.Generic[LIST_DATA]):
    meta: MetaResponse
    objects: typing.List[LIST_DATA]


class BaseListResponse(GenericModel, typing.Generic[LIST_DATA]):
    code: int = 200
    message: str = 'ok'
    data: ListResponseData[LIST_DATA]
