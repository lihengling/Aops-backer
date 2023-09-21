# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2023/03/24
"""
from aerich import Command

from OperationFrame.config import config


aer = Command(
    tortoise_config=config.MYSQL_TORTOISE_ORM,
    location=f"./{config.FRAME_NAME}/migrations/{config.ENV}",
)
