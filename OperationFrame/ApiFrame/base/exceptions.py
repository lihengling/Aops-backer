# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2023/03/03
"""
import typing
from http import HTTPStatus

from fastapi import Request, Response, HTTPException as FHTTPException
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as SHTTPException

from OperationFrame.ApiFrame.base.response import init_error_response
from OperationFrame.config import config
from OperationFrame.utils.log import logger_uru as logger
from OperationFrame.ApiFrame.base import ORJSONResponse
from OperationFrame.utils.models import BaseResponse
from OperationFrame.utils.json import dumps


@init_error_response
class BaseError(Exception):
    HTTPStatus = HTTPStatus.INTERNAL_SERVER_ERROR
    code: int = 500
    message: str = '方法内部错误'
    data: typing.Any = None

    model: BaseResponse

    def __init__(self, **kwargs):
        self.__dict__.update(**kwargs)

    @classmethod
    def get_response(cls, e=None) -> ORJSONResponse:
        if not e:
            e = cls()

        http_status = HTTPStatus(getattr(e, 'HTTPStatus', HTTPStatus.INTERNAL_SERVER_ERROR))
        return ORJSONResponse(BaseResponse(
            code=e.code,
            message=http_status.phrase + " | " + e.message,
            data=e.data,
        ), status_code=http_status.value)


@init_error_response
class BadRequestError(BaseError):
    HTTPStatus = HTTPStatus.BAD_REQUEST
    code = 400
    message = '请求无效'


@init_error_response
class AccessTokenExpire(BaseError):
    HTTPStatus = HTTPStatus.UNAUTHORIZED
    code = 401
    message = '用户认证失败'


@init_error_response
class ForbiddenError(BaseError):
    HTTPStatus = HTTPStatus.FORBIDDEN
    code = 403
    message = '权限不足'


@init_error_response
class NotFindError(BaseError):
    HTTPStatus = HTTPStatus.NOT_FOUND
    code = 404
    message = '内容不存在'


@init_error_response
class BaseValueError(BaseError):
    HTTPStatus = HTTPStatus.UNPROCESSABLE_ENTITY
    code = 422
    message = '参数有误，请检查请求参数'


# 忽略的异常类型
PASS_EXCEPTION = (AccessTokenExpire, ForbiddenError,)


async def exception_handler(request: Request, e: Exception) -> Response:
    if isinstance(e, (SHTTPException, FHTTPException)):
        return ORJSONResponse(
            BaseResponse(
                code=e.status_code,
                message=e.detail
            ),
            status_code=e.status_code
        )

    data = {
        "path": request.url.path,
        "body": None,
        "error": str(e)
    }

    if isinstance(e, BaseError):
        http_status = HTTPStatus(getattr(e, 'HTTPStatus', HTTPStatus.INTERNAL_SERVER_ERROR))
        response: BaseResponse = BaseResponse(
            code=e.code,
            message=http_status.phrase + " | " + e.message
        )
    elif isinstance(e, RequestValidationError):
        data['body'] = e.body
        new_e = BaseValueError()
        http_status = HTTPStatus(new_e.HTTPStatus)
        response: BaseResponse = BaseResponse(
            code=new_e.code,
            message=http_status.phrase + " | " + new_e.message
        )
        if config.SERVER_DEBUG:
            data['errors'] = e.errors()
    else:
        http_status = HTTPStatus(HTTPStatus.INTERNAL_SERVER_ERROR)
        response: BaseResponse = BaseResponse(
            code=http_status.value,
            message=http_status.phrase + " | " + str(e) if config.SERVER_DEBUG else BaseError.message
        )

    data.update({
        "code": response.code,
        "message": response.message,
        "scope": request.scope,
    })

    if not isinstance(e, (PASS_EXCEPTION, BaseError)):
        logger.exception(
            "path={path} code={code} message={message}\n"
            "scope={scope}\n"
            "body={body}",
            **{k: dumps(v, default=str) if isinstance(v, dict) else v for k, v in data.items()}
        )
    if getattr(e, 'data', None):
        response.data = e.data
    elif config.SERVER_DEBUG and not isinstance(e, PASS_EXCEPTION):
        response.data = {k: v for k, v in data.items() if k not in ['code', 'message', 'path']}

    response: Response = Response(
        dumps(response.dict(include={'code', 'message', 'data'}), default=str),
        status_code=http_status.value,
        media_type="application/json"
    )
    # 处于用户/角色认证模式时候，失败清除 cookie
    if isinstance(e, AccessTokenExpire) and config.VERIFY_TYPE_AUTH:
        response.delete_cookie("token")
        response.delete_cookie("username")

    return response
