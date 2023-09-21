# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2023/04/21
"""
import asyncio
from xmlrpc.client import Fault, loads
from xmlrpc.server import DocXMLRPCServer as BaseRPCServer, resolve_dotted_attribute, DocXMLRPCRequestHandler

from OperationFrame.ApiFrame.utils.rpc.exceptions import rpc_exception_handler
from OperationFrame.ApiFrame.utils.rpc.middleware import dispatch_events
from OperationFrame.ApiFrame.utils.rpc.utils import dumps
from OperationFrame.config import config
from OperationFrame.utils.log import logger
from OperationFrame.ApiFrame.utils.rpc.constant import RPC_NAME, RPC_TITLE, RPC_DOCUMENTATION


class RPCServer(BaseRPCServer):

    def __init__(
            self, addr, requestHandler=DocXMLRPCRequestHandler, logRequests=True, allow_none=True,
            encoding=None, bind_and_activate=False, use_builtin_types=False):
        super().__init__(addr, requestHandler, logRequests, allow_none, encoding, bind_and_activate, use_builtin_types)
        self.set_server_name(RPC_NAME)
        self.set_server_title(RPC_TITLE)
        self.set_server_documentation(RPC_DOCUMENTATION)

    def register_function(self, function=None, name=None):
        if self.funcs.get(name, None) is None:
            return super().register_function(function, name)
        logger.warning(f'rpc register_function {function.__name__} is conflict')

    @staticmethod
    async def run_dispatch(func, params):
        if asyncio.iscoroutinefunction(func):
            return await func(*params)
        else:
            return func(*params)

    @dispatch_events
    async def _dispatch(self, method, params, host=None):
        func = self.funcs.get(method, None)
        if func is not None:
            return await self.run_dispatch(func, params)

        if self.instance is not None:
            if hasattr(self.instance, '_dispatch'):
                return await super(self.instance)._dispatch(method, params)
            try:
                func = resolve_dotted_attribute(self.instance, method, self.allow_dotted_names)
            except AttributeError:
                pass
            else:
                return await self.run_dispatch(func, params)

        return None

    async def _marshaled_dispatch(self, data, dispatch_method=None, path=None, host=None):
        params, method = loads(data, use_builtin_types=self.use_builtin_types)
        try:
            response = await self._dispatch(method, params, host=host)
            response = dumps((response,), methodresponse=1, allow_none=self.allow_none, encoding=self.encoding)
        except Exception as err:
            if isinstance(err, Fault):
                response = dumps(err, allow_none=self.allow_none, encoding=self.encoding)
            else:
                response = await rpc_exception_handler(err, method, params, host)
                response = dumps((response,), methodresponse=1, allow_none=self.allow_none, encoding=self.encoding)

        return response.encode(self.encoding, 'xmlcharrefreplace')


rpc = RPCServer((config.SERVER_HOST, config.SERVER_PORT))
