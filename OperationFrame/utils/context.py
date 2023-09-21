# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2022/08/03
"""
from redis.client import Redis


class Context:
    tag:              str = None   # 运行中 tag
    log_id:           int = None   # 运行中 用于 log: open 的id
    pool:             str = None   # redis 操作池
    redis:          Redis = None   # redis 句柄
    redis_connected: bool = False  # redis 连接性

    depend_mysql:    bool = None   # 依赖 mysql
    depend_redis:    bool = None   # 依赖 redis


context = Context()
