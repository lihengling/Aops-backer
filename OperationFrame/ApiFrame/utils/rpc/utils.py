# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2023/04/24
"""
import xmlrpc.client
from xmlrpc.client import Marshaller as BaseMarshaller, escape, dumps


class Marshaller(BaseMarshaller):

    def __init__(self, encoding='utf-8', allow_none=True):
        super(Marshaller, self).__init__(encoding, allow_none)

    def dump_struct(self, value, write, escape=escape):
        value = {k: v for k, v in value.items() if not str(k).startswith('_') and not str(k).endswith('_')}
        super().dump_struct(value, write, escape)


xmlrpc.client.FastMarshaller = Marshaller
dumps = dumps
