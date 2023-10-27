# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2023/05/16
"""
import typing
from pydantic.generics import GenericModel
from pydantic import BaseModel as Model

from OperationFrame.utils.json import loads, dumps, DEFAULT_ENCODERS_BY_TYPE

DataT = typing.TypeVar('DataT')
DEFAULT_ENCODERS_BY_TYPE[Model] = lambda obj: obj.dict()


class BaseModel(Model):
    class Config:
        json_loads = loads
        json_dumps = dumps
        extra = 'allow'


class BaseResponse(GenericModel, typing.Generic[DataT]):
    code: int = 200
    message: str = 'ok'
    data: typing.Optional[DataT] = None


class BaseResponseList(BaseResponse, GenericModel, typing.Generic[DataT]):
    total: int


class JobResponse(BaseModel):
    job_id: str
