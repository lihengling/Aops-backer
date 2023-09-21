# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2023/03/30
"""
import os

from OperationFrame.config import config
from OperationFrame.ApiFrame.utils.arq import CTX, Worker
from OperationFrame.config.constant import TOML_DIR

STAT = os.stat(TOML_DIR)


@Worker.cron(second={s for s in range(1, 61, 1)}, summary='同步配置 | 1秒同步1次')
async def sync_config(ctx: CTX) -> None:
    global STAT
    re_stat = os.stat(TOML_DIR)
    if STAT.st_mtime != re_stat.st_mtime:
        config.init_property()
        STAT = re_stat
