# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2023/03/21
"""
from pydantic import RedisDsn
from typing import Optional

from OperationFrame.utils.models import BaseModel


class FrameLoader(BaseModel):
    ENV:                     Optional[str]                             # 当前环境字段
    MYSQL_DB:                Optional[str]                             # mysql 数据库名称
    MYSQL_PASS:              Optional[str]                             # mysql 数据库密码
    MYSQL_HOST:                        str = '127.0.0.1'               # mysql 数据库主机
    MYSQL_PORT:                        int = 3306                      # mysql 数据库端口
    MYSQL_USER:                        str = 'root'                    # mysql 数据库用户
    MYSQL_CHAR:                        str = 'utf-8'                   # mysql 数据库编码
    MYSQL_REGISTER_MODEL:   Optional[list]                             # mysql 注册模型
    MYSQL_MENU_MODEL:       Optional[list]                             # mysql 业务模型
    MYSQL_APPS_MODEL:       Optional[list]                             # mysql app模型
    MYSQL_ENGINE:           Optional[str]                              # mysql 引擎
    REDIS_DSN:              Optional[RedisDsn]                         # redis 连接
    WORKER_DB:                         str = '0'                       # redis 任务数据库名称
    WORKER_KEEP:                       int = 60 * 60                   # redis 任务数据库保留记录时间(单位: 秒)
    REDIS_DB:                          str = '1'                       # redis 其他信息数据库名称
    REDIS_SCHEMES:                     str = 'redis'                   # redis 数据库协议
    REDIS_SOCKET_TIMEOUT:    Optional[str]                             # redis 连接超时时间
    REDIS_PASS:              Optional[str]                             # redis 数据库密码
    REDIS_HOST:                        str = '127.0.0.1'               # redis 数据库主机
    REDIS_PORT:                        int = 6379                      # redis 数据库端口
    SERVER_HOST:                       str = '127.0.0.1'               # 服务端地址
    SERVER_PORT:                       int = 8080                      # 服务端端口
    SERVER_DEBUG:                     bool = False                     # 服务端是否debug模式
    SERVER_RELOAD:                    bool = False                     # 服务端是否重载模式
    SERVER_WORKER:                     int = 1                         # 服务端进程数
    SERVER_API_ALLOW:                 bool = False                     # 服务端 api 模式(提供http请求)
    SERVER_RPC_ALLOW:                 bool = False                     # 服务端 rpc 模式(提供rpc请求)
    SERVER_MOUNTED:                   bool = False                     # 服务端 是否挂载
    WORKER_MAX_JOBS:                   int = 15                        # 异步任务最大并发数
    WORKER_DSN:         Optional[RedisDsn]                             # 异步任务连接
    VERIFY_TYPE_KEY:                  bool = False                     # 是否启动校验头中间件
    VERIFY_TYPE_AUTH:                 bool = False                     # 是否启动角色验证(这将注册额外的表)
    MYSQL_TORTOISE_ORM:     Optional[dict]                             # tortoise 引擎
    LOGS_DIR_NAME:                     str = 'OperationLogs'           # 日志存放目录名称
    LOGS_ACCESS_SAVE:                  str = 3                         # 日志保留时间(单位: 天)
    LOGS_MULTI_DIR:          Optional[str] = 'OperationLogs'           # 并发任务日志存放目录
    LOGS_SUMMARY_DIR:        Optional[str] = 'OperationLogs'           # 警告日志汇总存放目录
    LOGS_WORKER_DIR:         Optional[str] = 'OperationLogs'           # worker 任务日志过程存放目录
    WHITE_IPS:                        list = ['127.0.0.1']             # 请求白名单
    WHITE_IPS_OPEN:                   bool = False                     # 是否启用ip白名单限制
    TASK_DEFAULT_WORKER:               str = 20                        # 并发任务默认并发数
    TASK_MAX_WORKER:                  list = []                        # 定义并发任务特定最大并发数列表
    WS_HEART_BEAT_TIME:                int = 10                        # ws 接口心跳频率检测时间


class ServiceLoader(BaseModel):
    ...
