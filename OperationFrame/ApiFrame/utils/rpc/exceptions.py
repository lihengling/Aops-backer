# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2023/03/03
"""
from http import HTTPStatus

from fastapi import HTTPException as FHTTPException
from starlette.exceptions import HTTPException as SHTTPException

from OperationFrame.ApiFrame.base.exceptions import BaseError, BaseValueError, ForbiddenError
from OperationFrame.config import config
from OperationFrame.ApiFrame.base import ORJSONResponse
from OperationFrame.utils.models import BaseResponse


async def rpc_exception_handler(e: Exception, method, params, host=None):
    if isinstance(e, (SHTTPException, FHTTPException)):
        return ORJSONResponse(
            BaseResponse(
                code=e.status_code,
                message=e.detail
            ),
            status_code=e.status_code
        )

    data = {
        "method": method,
        "params": params,
    }

    if isinstance(e, BaseError):
        http_status = HTTPStatus(getattr(e, 'HTTPStatus', HTTPStatus.INTERNAL_SERVER_ERROR))
        response: BaseResponse = BaseResponse(
            code=e.code,
            message=http_status.phrase + " | " + e.message
        )
        if isinstance(e, ForbiddenError):
            data['host'] = host
    elif isinstance(e, (AttributeError, TypeError)):
        new_e = BaseValueError()
        http_status = HTTPStatus(new_e.HTTPStatus)
        response: BaseResponse = BaseResponse(
            code=new_e.code,
            message=http_status.phrase + " | " + str(e) if config.SERVER_DEBUG else new_e.message
        )
    else:
        http_status = HTTPStatus(HTTPStatus.INTERNAL_SERVER_ERROR)
        response: BaseResponse = BaseResponse(
            code=http_status.value,
            message=http_status.phrase + " | " + str(e) if config.SERVER_DEBUG else BaseError.message
        )

    if config.SERVER_DEBUG:
        response.data = {k: v for k, v in data.items() if k not in ['code', 'message', 'path']}

    return response
