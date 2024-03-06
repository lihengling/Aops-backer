# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2023/07/04
"""
from fastapi import Query
from pydantic import BaseModel

from OperationFrame.config import config


class PageQuery(BaseModel):
    pageIndex: int = Query(1, description='页码')
    pageSize:  int = Query(config.PAGE_SIZE, description='返回条目')
    query:     str = Query(None, description='模糊查询参数')
