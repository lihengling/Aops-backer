# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2023/03/03
"""
from typing import Union
from OperationFrame.ApiFrame.base import router_index
from OperationFrame.utils.models import BaseModel, BaseResponse
from OperationFrame.utils.context import context


class PongResponse(BaseModel):
    ping: Union[int, str, None] = None


@router_index.get("/ping", summary="测试服务端是否正常", response_model=BaseResponse[PongResponse])
def ping():
    """ 测试服务端是否正常 """
    return BaseResponse[PongResponse](
        data=PongResponse(ping=context.redis.incr('ping') if context.redis else None)
    )
