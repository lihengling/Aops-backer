# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2023/04/21
"""
import xmlrpc.client

proxy = xmlrpc.client.ServerProxy("http://localhost:8080/rpc")
result = proxy.ping()
print(result)
