# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2023/03/17
"""
import typing as t

from .constant import TAG_DEFAULT
from OperationFrame.utils.models import BaseModel, BaseResponse


TASK = t.TypeVar('TASK')


class MetaRoute(BaseModel):
    name:         str
    path:         str
    tags:         list
    methods:      list
    response_model: t.Type[BaseResponse]


class MenuTask(BaseModel):
    name:         str
    sign:         str
    tag:          str
    log:          bool
    params:       str
    self:         TASK
    mounted:      bool
    depend_mysql: bool
    depend_redis: bool
    route: t.Optional[MetaRoute] = None


class BaseMeta:
    # 任务名称
    name:          str = '未定义'
    # 任务标识
    sign:          str = ''
    # 任务标签
    tag:           str = TAG_DEFAULT
    # 任务是否挂载，若不挂载无法使用
    mounted:      bool = True
    # 任务是否依赖 mysql，若不依赖不连接 mysql
    depend_mysql: bool = True
    # 任务是否依赖 redis，若不依赖不连接 redis
    depend_redis: bool = False
    # 任务是否记录任务过程
    log:          bool = False
    # 任务是否注册成接口，一旦定义则提供一个以 MetaRoute 为数据集(其他参数请参考app的路由注册方式)的接口
    route: t.Optional[MetaRoute] = None
    # 任务是否定义为以cbv为run方法的执行方式，一旦定义则无需定义run方法
    func: t.Union[t.List[t.Union[t.Callable, t.Awaitable]], t.Callable, t.Awaitable] = None
