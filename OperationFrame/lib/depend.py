# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2023/07/04
"""
from typing import Any, Optional
from fastapi import Depends

from OperationFrame.ApiFrame.base.exceptions import BaseValueError


def paginate_factory(max_limit: Optional[int] = None) -> Any:
    """
    分页依赖
    """
    def paginate(skip: int = 0, limit: Optional[int] = max_limit):
        if skip < 0:
            raise BaseValueError(message='skip 跳过参数数量必须大于或等于 0')

        if limit is not None:
            if limit <= 0:
                raise BaseValueError(message='limit 限制查询参数必须大于 0')
            elif max_limit and max_limit < limit:
                raise BaseValueError(message=f'limit 限制查询参数必须小于 {max_limit}')

        return {"skip": skip, "limit": limit}

    return Depends(paginate)
