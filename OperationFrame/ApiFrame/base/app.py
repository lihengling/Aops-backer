# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2022/08/03
"""
import typing
from fastapi import FastAPI
from fastapi.datastructures import Default
from fastapi.responses import Response

from OperationFrame.ApiFrame.base.constant import ROUTER_START_SWITCH
from OperationFrame.utils.json import dumps


class ORJSONResponse(Response):
    media_type = "application/json"

    def render(self, content: typing.Any) -> bytes:
        return dumps(content, decode=False)


app = FastAPI(
    docs_url=f'{ROUTER_START_SWITCH}/docs',
    redoc_url=f'{ROUTER_START_SWITCH}/redoc',
    openapi_url=f'{ROUTER_START_SWITCH}/openapi.json',
    default_response_class=Default(ORJSONResponse)
)
