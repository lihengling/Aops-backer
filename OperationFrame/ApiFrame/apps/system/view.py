# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2023/06/29
"""
import asyncio
import glob
import os
import time
import jwt
from typing import List

from arq.constants import in_progress_key_prefix, default_queue_name, abort_jobs_ss
from arq.jobs import JobDef
from fastapi import WebSocket, Security
from fastapi.security.utils import get_authorization_scheme_param
from jwt import PyJWTError
from pydantic import ValidationError
from starlette.websockets import WebSocketState
from websockets.exceptions import ConnectionClosedOK

from OperationFrame.ApiFrame.apps.user.models import User
from OperationFrame.ApiFrame.base.security import AUTH_SCHEME, AUTH_HEADER
from OperationFrame.ApiFrame.utils.arq.schema import JobStatus
from OperationFrame.ApiFrame.base import router_system, NotFindError, PERMISSION_INFO, PERMISSION_UPDATE
from OperationFrame.ApiFrame.base import constant
from OperationFrame.ApiFrame.utils.arq import Worker
from OperationFrame.ApiFrame.utils.jwt import check_permissions
from OperationFrame.config import config
from OperationFrame.lib.depend import paginate_factory
from OperationFrame.lib.tools import paginate_list, get_file
from OperationFrame.utils.models import BaseResponse
from OperationFrame.utils.context import context


@router_system.get("/worker/ping", summary="worker 是否正常", response_model=BaseResponse,
                   dependencies=[Security(check_permissions, scopes=[f'worker_{PERMISSION_INFO}'])])
async def worker_ping():
    job = await context.pool.enqueue_job('ping_task', 'message')
    return BaseResponse(data=job.job_id)


@router_system.post("/worker/abort", summary="worker 任务终止", response_model=BaseResponse,
                   dependencies=[Security(check_permissions, scopes=[f'worker_{PERMISSION_UPDATE}'])])
async def worker_abort(job_id: str):
    if await context.pool.exists(f"{in_progress_key_prefix}{job_id}"):
        await context.pool.zrem(default_queue_name, job_id)
        await context.pool.zadd(default_queue_name, {job_id: 1})
        await context.pool.zadd(abort_jobs_ss, {job_id: int(time.time() * 1000)})
        return BaseResponse(data=f'{job_id} 已终止')
    else:
        raise NotFindError(message=f'{job_id} 已完成或不存在')


@router_system.get("/worker", summary="worker 任务列表", response_model=BaseResponse[List[JobStatus]],
                   dependencies=[Security(check_permissions, scopes=[f'worker_{PERMISSION_INFO}'])])
async def worker(pagination: dict = paginate_factory()):
    req: List[JobStatus] = []
    result_jobs = await context.pool.all_job_results()
    queued_jobs = await context.pool.keys(f'{in_progress_key_prefix}*')
    queued_values = await context.pool.mget(queued_jobs)

    for job in result_jobs:
        req.append(JobStatus(job_id=job.job_id, job_name=Worker.get_job_name(job.function), success=job.success,
                             job_params=f"{str(job.args)} | {str(job.kwargs)}", result=job.result,
                             start_time=job.start_time.timestamp(), finish_time=job.finish_time.timestamp(),
                             queue_name=job.queue_name))
    for job_b, value_b in zip(queued_jobs, queued_values):
        job = job_b.decode()
        if 'cron' not in job:
            job_id = job.split(in_progress_key_prefix, 1)[-1]
            job_def: JobDef = await context.pool._get_job_def(job_id.encode(), None)
            req.append(JobStatus(start_time=job_def.enqueue_time.timestamp(), job_name=value_b.decode(),
                                 job_params=f"{str(job_def.args)} | {str(job_def.kwargs)}", job_id=job.split(':')[-1]))

    return BaseResponse(data=paginate_list(req, pagination['skip'], pagination['limit']))


@router_system.websocket("/worker/ws/{job_id}", name="worker 任务日志")
async def job_logs(ws: WebSocket, job_id: str):
    await ws.accept()

    # 校验token
    success = True
    authorization = ws.headers.get(AUTH_HEADER, '')
    scheme, param = get_authorization_scheme_param(authorization)
    if not authorization or scheme.lower() != AUTH_SCHEME:
        success = False
    try:
        payload = jwt.decode(param, constant.JWT_SECRET_KEY, algorithms=[constant.JWT_ALGORITHM])
        username = payload.get('username', None)
        password = payload.get('password', None)
        if not payload or username is None or password is None:
            success = False
    except (PyJWTError, ValidationError, jwt.InvalidTokenError, jwt.ExpiredSignatureError):
        success = False
        username = None

    # 检查用户
    user = await User().get_or_none(username=username)
    if not user or user.is_active is False or not success:
        await ws.send_text(f'token校验用户失败')
        await ws.close()
        ws.application_state = WebSocketState.DISCONNECTED
        return

    # 推送日志
    job_path = f'{config.LOGS_WORKER_DIR}/*{job_id}*'
    job_list = glob.glob(job_path)

    if not job_list:
        await ws.send_text(f'{job_id} 不存在')
        await ws.close()
        ws.application_state = WebSocketState.DISCONNECTED
        return
    else:
        job_file = job_list[0]
        job_stat = os.stat(job_file)

    send_num: int = 0
    try_time: int = 0
    while ws.application_state == WebSocketState.CONNECTED:
        res_stat = os.stat(job_file)
        try_time += 1

        if job_stat.st_mtime != res_stat.st_mtime or send_num == 0:
            line = await get_file(job_file)
            line = line[send_num:]
            send_num += len(line)
            job_stat = res_stat

            finish = False
            for data in line:
                await ws.send_text(data)
                if 'RunTime' in data:
                    finish = True
            if finish:
                break

        if try_time % config.WS_HEART_BEAT_TIME == 0:
            try:
                await ws.send_text('heartbeat')
            except ConnectionClosedOK:
                break

        await asyncio.sleep(2)

    await ws.close()
    ws.application_state = WebSocketState.DISCONNECTED
