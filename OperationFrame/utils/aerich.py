# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2023/03/24
"""
import os
from aerich import Command

from OperationFrame.config import config


location = f"./{config.FRAME_NAME}/migrations/{config.ENV}"

if not os.path.exists(location):
    os.makedirs(location)

aer = Command(tortoise_config=config.MYSQL_TORTOISE_ORM, location=location)
