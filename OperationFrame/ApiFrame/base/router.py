# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2023/03/03
"""
from fastapi import APIRouter as BaseAPIRouter

from OperationFrame.ApiFrame.base.constant import ROUTER_SORT_APP, ROUTER_SORT_DEFAULT, ROUTER_START_SWITCH

Routers = []


class APIRouter(BaseAPIRouter):
    def __init__(self, *args, sort: str = ROUTER_SORT_DEFAULT, **kwargs):
        super(APIRouter, self).__init__(*args, **kwargs)
        self.sort = sort
        self.prefix = f"{ROUTER_START_SWITCH}{self.prefix}"
        Routers.append(self)


router_index:   APIRouter = APIRouter(prefix="")
router_user:    APIRouter = APIRouter(prefix="/user", tags=["User"], sort=ROUTER_SORT_APP)
router_game:    APIRouter = APIRouter(prefix="/game", tags=["Game"])
router_system:  APIRouter = APIRouter(prefix="/system", tags=["System"])
