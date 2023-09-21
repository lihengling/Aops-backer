# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2023/04/25
"""
from OperationFrame.config import config
from OperationFrame.ApiFrame.base.exceptions import ForbiddenError, BadRequestError


def dispatch_events(func):
    async def wrapper(*args, **kwargs):
        host: str = kwargs.get('host', None)
        if host and host not in config.WHITE_IPS:
            raise ForbiddenError
        response = await func(*args, **kwargs)
        if response is None:
            raise BadRequestError
        return response
    return wrapper
