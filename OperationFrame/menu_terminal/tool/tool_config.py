# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2023/03/16
"""
import glob

import redis
from redis.asyncio import Redis
from tortoise import Tortoise

from OperationFrame.config import config
from OperationFrame.utils.aerich import aer
from OperationFrame.utils.cbvmenu import CommonCbv
from OperationFrame.utils.connecter import cmd_result
from OperationFrame.utils.log import logger


class ToolConfigStatus(CommonCbv):

    async def run(self):
        for k, v in config.config_property.items():
            print(f"{k:<20} => {v}")

    class Meta:
        name = '工具 配置项状态'
        sign = 'tool_config_status'
        tag = 'Tool'
        depend_mysql = False


class ToolConfigCheck(CommonCbv):

    check_python: str = 'python3 -V'
    check_pip:    str = 'pip check requirements.txt'

    async def run(self):
        # python 3.10+
        logger.info('开始检测 python 运行版本...')
        req = await cmd_result(self.check_python)
        req = str(req).strip()
        if req:
            main, branch = req.split(' ')[1].split('.')[0:2]
            logger.info(f'当前版本: {req}, 推荐版本: 3.10+')
            if int(main) >= 3 and int(branch) >= 8:
                logger.debug(f'python 版本: PASS')
            else:
                logger.error('python 运行版本不能低于 3.8')
                logger.error(f'python 版本: FAIL')
        else:
            logger.error('检测 python 版本: FAIL | 请检测 python 环境')

        # 检测pip依赖包
        req = await cmd_result(self.check_pip)
        logger.info(f'开始检测 pip 依赖包环境...\n{str(req).strip()}')

        # 检测数据库连接是否正常
        logger.info('开始检测 数据库 连接状态...')
        logger.info(f'DB_NAME: {config.MYSQL_DB} | DB_USER: {config.MYSQL_USER} | DB_HOST: {config.MYSQL_HOST} | '
                    f'DB_PORT: {config.MYSQL_PORT} | DB_PASS: {config.MYSQL_PASS}')
        if Tortoise._inited:
            logger.debug(f'数据库 连接状态: PASS')
        else:
            logger.error(f'数据库 连接状态: FAIL')

        # 检查 redis 连接是否正常
        logger.info('开始检测 redis 连接状态...')
        _redis = await Redis.from_url(config.WORKER_DSN)
        try:
            await _redis.ping()
            logger.debug(f'redis 连接状态: PASS')
        except redis.exceptions.AuthenticationError:
            logger.error(f'redis 连接状态: FAIL')

        # 检测数据库是否初始化
        logger.info('开始检测 数据库 初始化状态...')
        files = glob.glob(f'{aer.location}/models/*_init.sql')
        if files:
            logger.info(f'数据库结构已初始化, 若表结构未生成, 尝试删除 {aer.location} 目录, 重新初始化')
            logger.debug(f'数据库 初始化状态: PASS')
        else:
            logger.error(f'数据库结构未初始化, 请尝试初始化, 并检查 {aer.location} 目录')
            logger.error(f'数据库 初始化状态: FAIL')

    class Meta:
        name = '工具 项目必要运行环境检测'
        sign = 'tool_config_check'
        tag = 'Tool'
        depend_mysql = True
        depend_redis = True
