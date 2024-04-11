# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2023/03/03
"""
import typing
from json.decoder import JSONDecodeError
from time import time
from uuid import uuid4

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp
from fastapi.middleware.cors import CORSMiddleware as BaseCORSMiddleware

from OperationFrame.ApiFrame.base import ORJSONResponse
from OperationFrame.ApiFrame.base.constant import SECRET_KEY
from OperationFrame.ApiFrame.base.exceptions import BadRequestError, ForbiddenError
from OperationFrame.config import config
from OperationFrame.config.constant import SERVER_TAG_HTTP
from OperationFrame.lib.tools import verify_key
from OperationFrame.utils.log import logger
from OperationFrame.ApiFrame.utils.rpc import rpc
from OperationFrame.ApiFrame.utils.rpc.constant import RPC_DOCS_URL, RPC_START_SWITCH
from OperationFrame.utils.models import BaseResponse

Middleware = []


def add_wrapper(cls):
    def wrapper(*args, **kwargs):
        return cls(*args, **kwargs)

    if getattr(cls, 'using', True):
        Middleware.append((getattr(cls, 'name', None) or cls.__name__, cls))
    return wrapper


async def set_body(request: Request):
    res = await request._receive()

    async def receive():
        return res
    request._receive = receive


@add_wrapper
class CORSMiddleware(BaseCORSMiddleware):
    """ http: 跨域处理 """
    app:    ASGIApp
    name:       str = 'cors'
    using:     bool = config.SERVER_TYPE == SERVER_TAG_HTTP

    def __init__(
        self,
        app: ASGIApp,
        allow_origins: typing.Sequence[str] = ("*",),
        allow_methods: typing.Sequence[str] = ("*",),
        allow_headers: typing.Sequence[str] = ("*",),
        allow_credentials: bool = True,
        allow_origin_regex: typing.Optional[str] = None,
        expose_headers: typing.Sequence[str] = (),
        max_age: int = 600,
    ) -> None:
        super().__init__(app, allow_origins, allow_methods, allow_headers, allow_credentials,
                         allow_origin_regex, expose_headers, max_age)


@add_wrapper
class WhiteListMiddleware(BaseHTTPMiddleware):
    """ rpc or http: 流量白名单限制 """
    app: ASGIApp
    name:    str = 'White List'
    using:  bool = config.WHITE_IPS_OPEN

    async def dispatch(self,
                       request: Request, call_next: RequestResponseEndpoint) -> typing.Union[BaseResponse, Response]:
        if request.client.host not in config.WHITE_IPS:
            return ORJSONResponse(
                BaseResponse(data='ip 禁止访问', code=BadRequestError.code, message=BadRequestError.message))
        response = await call_next(request)
        return response


@add_wrapper
class RPCORHTTPMiddleware(BaseHTTPMiddleware):
    """ rpc or http 路由转向 """
    app: ASGIApp
    name:    str = 'RoP'

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.url.path.startswith(RPC_START_SWITCH):
            if request.url.path == RPC_DOCS_URL:
                return Response(content=rpc.generate_html_documentation())
            data = await request.body()
            response = await rpc._marshaled_dispatch(data, host=request.client.host)
            return Response(content=response, media_type="text/xml")
        else:
            return await call_next(request)


@add_wrapper
class BodyHandleMiddleware(BaseHTTPMiddleware):
    """ rpc or http: body 处理器 """
    app: ASGIApp
    name:            str = 'Body Handler'
    no_verify_path: list = ['/openapi.json', '/docs', '/redoc']

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        await set_body(request)
        try:
            body:   dict = await request.json()
        except JSONDecodeError:
            body:   dict = {}
        before:     time = time()
        trace_data: dict = {
            'Ts-Request-Id': request.headers.get('Ts-Request-Id', str(uuid4())),
        }

        with logger.contextualize(**trace_data):
            logger.info(f'<{request.client.host}> - {request.method} - {request.url} - {body}')

        if config.VERIFY_TYPE_KEY and request.url.path not in self.no_verify_path:
            res = body if request.method in ['POST'] else request.query_params
            _sign = res.get('sign', '')
            _time = res.get('time', '0')
            if not verify_key(SECRET_KEY, _sign, _time):
                return ORJSONResponse(
                    BaseResponse(data='key校验失败', code=ForbiddenError.code, message=ForbiddenError.message))

        response: Response = await call_next(request)
        after = time()
        response.headers.update({
            'X-Request-After': str(after),
            'X-Request-Before': str(before),
            'X-Response-Time': str(after - before),
            **trace_data
        })
        return response
