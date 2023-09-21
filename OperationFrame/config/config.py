# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2022/07/19
"""
import os
import json
import toml
import pydantic
from pathlib import Path
from typing import Any, List, Union
from redis import Redis, AuthenticationError

from OperationFrame.utils.models import BaseModel
from OperationFrame.config.constant import CACHES_CONFIG_KEY, TOML_DIR, ENV_NAME, ENV_DEV
from OperationFrame.config.extend import extend_property
from OperationFrame.config.schema import FrameLoader, ServiceLoader
from OperationFrame.utils.context import context


class BaseConfig(BaseModel):
    """
    config 基础配置
    """
    PROJECT_PATH:      Path = Path(__file__).parent.parent.resolve()   # 项目根目录
    FRAME_NAME:         str = PROJECT_PATH.name                        # 框架名称
    TERMINAL_VIEW_DIR: list = [                                        # 终端菜单视图目录
        'menu_terminal'
    ]
    SERVER_VIEWS_DIR:  dict = {                                        # 接口加载模块
        'view': 'ApiFrame.apps',                                       # 接口加载模块：app 接口
        'task': 'ApiFrame.worker.task',                                # 接口加载模块：app 异步任务接口
        'cron': 'ApiFrame.worker.cron',                                # 接口加载模块：app 计划任务接口
    }

    def __init__(self, models: List = None):
        super().__init__()
        self.config_property = dict()
        self.init_property(models)

    def __getitem__(self, item) -> Any:
        if context.redis_connected:
            config_caches = context.redis.get(CACHES_CONFIG_KEY)
            config_caches = json.loads(config_caches)
            return config_caches.get(item, None)
        return self.config_property.get(item, None)

    def __getattr__(self, item) -> Any:
        return self.__getitem__(item)

    def init_property(self, models: Union[List, None] = None):
        # 加载model默认配置
        if models:
            for model in models:
                model_dict = model().dict()
                try:
                    for key, value in model_dict.items():
                        if key == key.upper() and value is not None:
                            self.config_property[key] = value
                except pydantic.error_wrappers.ValidationError:
                    continue
        # 加载toml配置
        loader = toml.load(TOML_DIR)
        for sign, value in loader.items():
            if '-' in sign and env in sign or '-' not in sign:
                for e_key, e_value in value.items():
                    if e_key == e_key.upper():
                        self.config_property[e_key] = e_value
        # 加载计算配置
        self.config_property = extend_property(self.config_property)
        if context.redis is None:
            context.redis = Redis.from_url(self.WORKER_DSN)
        try:
            context.redis.set(CACHES_CONFIG_KEY, json.dumps(self.config_property))
        except (AuthenticationError, ConnectionError, ValueError):
            pass


env = os.getenv(ENV_NAME, ENV_DEV).upper()
config = BaseConfig(models=[FrameLoader, ServiceLoader])
