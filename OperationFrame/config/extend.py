# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2023/04/10
"""
import os
import sys
import pydantic
from urllib.parse import quote_plus


platform = sys.platform


def extend_property(bc: dict) -> dict:
    # 加载 mysql 引擎
    bc['MYSQL_ENGINE'] = f"mysql://{bc['MYSQL_USER']}:{bc['MYSQL_PASS']}@{bc['MYSQL_HOST']}:" \
                                  f"{bc['MYSQL_PORT']}/{bc['MYSQL_DB']}"

    # 加载 模型
    if not bc.get('MYSQL_APPS_MODEL', None) or not bc.get('MYSQL_MENU_MODEL', None):
        bc['MYSQL_MENU_MODEL'], bc['MYSQL_APPS_MODEL'] = get_models()
    register = bc['MYSQL_MENU_MODEL'] + bc['MYSQL_APPS_MODEL'] if bc['VERIFY_TYPE_AUTH'] else bc['MYSQL_MENU_MODEL']
    bc['MYSQL_REGISTER_MODEL'] = register

    # 加载 tortoise 引擎
    MYSQL_TORTOISE_ORM = {
        "connections": {"default": bc['MYSQL_ENGINE']},
        "apps": {
            "models": {
                "models": ["aerich.models"] + register,
                "default_connection": "default",
            },
        },
        'use_tz': True,
        'timezone': 'Asia/Shanghai'
    }
    bc['MYSQL_TORTOISE_ORM'] = MYSQL_TORTOISE_ORM

    # 加载 redis dsn
    bc['REDIS_DSN'] = pydantic.RedisDsn(
            f"{bc['REDIS_SCHEMES']}://:{bc['REDIS_PASS']}@{quote_plus(bc['REDIS_HOST'])}"
            f":{bc['REDIS_PORT']}/{bc['REDIS_DB']}", scheme=bc['REDIS_SCHEMES'])

    # 加载 worker dsn
    bc['WORKER_DSN'] = pydantic.RedisDsn(
            f"{bc['REDIS_SCHEMES']}://:{bc['REDIS_PASS']}@{quote_plus(bc['REDIS_HOST'])}"
            f":{bc['REDIS_PORT']}/{bc['WORKER_DB']}", scheme=bc['REDIS_SCHEMES'])

    return bc


def get_models() -> tuple:
    menu_models:     list = ["OperationFrame.models"]
    apps_models:     list = []

    platform_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    if platform == 'win32':
        platform_dir += '\\ApiFrame\\apps'
    else:
        platform_dir += '/ApiFrame/apps'

    for path, _, files in os.walk(platform_dir):
        for file in files:
            if file == 'models.py':
                path = path.split(os.getcwd())[-1]
                path = path.replace('/', '.') if platform != 'win32' else path.replace('\\', '.')
                apps_models.append(f"{path.lstrip('.')}.{file.split('.')[0]}")

    return menu_models, apps_models
