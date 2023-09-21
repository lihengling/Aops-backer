# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2023/03/30
"""
from OperationFrame.ApiFrame.utils.arq import CTX, Worker
from OperationFrame.utils.log import logger


@Worker.task(summary='ping worker')
async def ping_task(ctx: CTX, msg: str) -> str:
    logger.debug(f"job_id {ctx['job_id']}, message: {msg}")
    return ctx['job_id']
