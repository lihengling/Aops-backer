# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2022/07/19
"""
from OperationFrame.utils.log import logger


async def start(srv_id):
    logger.info(f'{srv_id} 启动成功')
    return True
