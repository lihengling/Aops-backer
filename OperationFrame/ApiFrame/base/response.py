# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2023/03/09
"""
import typing

from pydantic import create_model

from OperationFrame.utils.models import BaseResponse
from OperationFrame.ApiFrame.base import app


def init_error_response(cls: typing.Type[Exception]) -> typing.Type[Exception]:
    """
    创建错误响应
    注意：错误响应模型必须 raise 不能 return
    """
    cls.model = create_model(
        cls.__name__ + "Model",
        code=getattr(cls, 'code', 500),
        message=getattr(cls, 'message', '方法内部错误'),
        __base__=BaseResponse,
    )
    app.router.responses[getattr(cls, 'code', 500)] = {'model': cls.model}
    return cls
