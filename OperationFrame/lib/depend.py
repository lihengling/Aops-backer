# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2023/07/04
"""
from typing import Any, Optional

from fastapi import Depends


def paginate_list_factory(max_limit: Optional[int] = None) -> Any:
    """
    创建列表分页依赖
    """

    def paginate(skip: int = 0, limit: Optional[int] = max_limit):
        if skip < 0:
            raise ValueError("Skip must be greater than or equal to zero")

        if limit is not None:
            if limit <= 0:
                raise ValueError("limit query parameter must be greater then zero")
            elif max_limit and max_limit < limit:
                raise ValueError(f"limit query parameter must be less then {max_limit}")

        return {"skip": skip, "limit": limit}

    return Depends(paginate)
