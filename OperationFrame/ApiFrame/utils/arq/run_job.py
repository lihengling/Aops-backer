# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2023/06/20
"""
import asyncio
from typing import Tuple, Any, Dict, Union, Optional, List

from arq import Worker as BaseWorker
from arq.constants import job_key_prefix, retry_key_prefix, abort_jobs_ss, keep_cronjob_progress, in_progress_key_prefix
from arq.cron import CronJob
from arq.jobs import serialize_result, logger, deserialize_job_raw, SerializationError, JobDef
from arq.utils import timestamp_ms, ms_to_datetime, args_to_string, truncate
from arq.worker import JobExecutionFailed, Function, no_result, Retry, RetryJob
from redis.exceptions import ResponseError, WatchError

from OperationFrame.utils.log import logger as frame_logger
from OperationFrame.utils.context import context
from OperationFrame.utils.scheduler_task import SchedulerTasksStatus


class Worker(BaseWorker):
    tasks_list:  Dict[str, Tuple] = {}

    @classmethod
    def get_job_name(cls, job_def: str) -> str:
        return cls.tasks_list.get(job_def, (None, job_def))[1]

    async def run_job(self, job_id: str, score: int) -> None:
        start_ms = timestamp_ms()
        async with self.pool.pipeline(transaction=True) as pipe:
            pipe.get(job_key_prefix + job_id)
            pipe.incr(retry_key_prefix + job_id)
            pipe.expire(retry_key_prefix + job_id, 88400)
            if self.allow_abort_jobs:
                pipe.zrem(abort_jobs_ss, job_id)
                v, job_try, _, abort_job = await pipe.execute()
            else:
                v, job_try, _ = await pipe.execute()
                abort_job = False

        function_name, enqueue_time_ms = '<unknown>', 0
        args: Tuple[Any, ...] = ()
        kwargs: Dict[Any, Any] = {}

        async def job_failed(exc: BaseException) -> None:
            self.jobs_failed += 1
            result_data_ = serialize_result(
                function=function_name,
                args=args,
                kwargs=kwargs,
                job_try=job_try,
                enqueue_time_ms=enqueue_time_ms,
                success=False,
                result=exc,
                start_ms=start_ms,
                finished_ms=timestamp_ms(),
                ref=f'{job_id}:{function_name}',
                serializer=self.job_serializer,
                queue_name=self.queue_name,
            )
            await asyncio.shield(self.finish_failed_job(job_id, result_data_))

        if not v:
            logger.warning('job %s expired', job_id)
            return await job_failed(JobExecutionFailed('job expired'))

        try:
            function_name, args, kwargs, enqueue_job_try, enqueue_time_ms = deserialize_job_raw(
                v, deserializer=self.job_deserializer
            )
        except SerializationError as e:
            logger.exception('deserializing job %s failed', job_id)
            return await job_failed(e)

        if abort_job:
            t = (timestamp_ms() - enqueue_time_ms) / 1000
            logger.info('%6.2fs ⊘ %s:%s aborted before start', t, job_id, function_name)
            return await job_failed(asyncio.CancelledError())

        try:
            function: Union[Function, CronJob] = self.functions[function_name]
        except KeyError:
            logger.warning('job %s, function %r not found', job_id, function_name)
            return await job_failed(JobExecutionFailed(f'function {function_name!r} not found'))

        if hasattr(function, 'next_run'):
            # cron_job
            ref = function_name
            keep_in_progress: Optional[float] = keep_cronjob_progress
        else:
            ref = f'{job_id}:{function_name}'
            keep_in_progress = None

        if enqueue_job_try and enqueue_job_try > job_try:
            job_try = enqueue_job_try
            await self.pool.setex(retry_key_prefix + job_id, 88400, str(job_try))

        max_tries = self.max_tries if function.max_tries is None else function.max_tries
        if job_try > max_tries:
            t = (timestamp_ms() - enqueue_time_ms) / 1000
            logger.warning('%6.2fs ! %s max retries %d exceeded', t, ref, max_tries)
            self.jobs_failed += 1
            result_data = serialize_result(
                function_name,
                args,
                kwargs,
                job_try,
                enqueue_time_ms,
                False,
                JobExecutionFailed(f'max {max_tries} retries exceeded'),
                start_ms,
                timestamp_ms(),
                ref,
                self.queue_name,
                serializer=self.job_serializer,
            )
            return await asyncio.shield(self.finish_failed_job(job_id, result_data))

        result = no_result
        exc_extra = None
        finish = False
        timeout_s = self.job_timeout_s if function.timeout_s is None else function.timeout_s
        incr_score: Optional[int] = None
        job_ctx = {
            'job_name': function_name,
            'job_id': job_id,
            'job_try': job_try,
            'enqueue_time': ms_to_datetime(enqueue_time_ms),
            'score': score,
        }
        ctx = {**self.ctx, **job_ctx}

        if self.on_job_start:
            await self.on_job_start(ctx)

        start_ms = timestamp_ms()
        success = False
        with frame_logger.contextualize(job_id=job_id):  # 把 job_id 设置到上下文
            try:
                s = args_to_string(args, kwargs)
                extra = f' try={job_try}' if job_try > 1 else ''
                if (start_ms - score) > 1200:
                    extra += f' delayed={(start_ms - score) / 1000:0.2f}s'
                logger.info('%6.2fs → %s(%s)%s', (start_ms - enqueue_time_ms) / 1000, ref, s, extra)
                self.job_tasks[job_id] = task = self.loop.create_task(function.coroutine(ctx, *args, **kwargs))

                try:
                    result = await asyncio.wait_for(task, timeout_s)
                except (Exception, asyncio.CancelledError) as e:
                    exc_extra = getattr(e, 'extra', None)
                    if callable(exc_extra):
                        exc_extra = exc_extra()
                    err_message = f"job_name: {function_name} | job_id: {job_id} | " \
                                  f"params: {str(kwargs)} + {str(args)} | job_error: {type(e)}{e}"
                    if isinstance(e, asyncio.CancelledError):
                        frame_logger.warning(f"{err_message}, Task Abort")
                    else:
                        frame_logger.error(err_message)
                        frame_logger.error(f'\n'.join([str(x) for x in task.get_stack()]))
                    raise
                else:
                    result_str = '' if result is None or not self.log_results else truncate(repr(result))
                finally:
                    del self.job_tasks[job_id]

            except (Exception, asyncio.CancelledError) as e:
                finished_ms = timestamp_ms()
                t = (finished_ms - start_ms) / 1000
                if self.retry_jobs and isinstance(e, Retry):
                    incr_score = e.defer_score
                    logger.info('%6.2fs ↻ %s retrying job in %0.2fs', t, ref, (e.defer_score or 0) / 1000)
                    if e.defer_score:
                        incr_score = e.defer_score + (timestamp_ms() - score)
                    self.jobs_retried += 1
                elif job_id in self.aborting_tasks and isinstance(e, asyncio.CancelledError):
                    logger.info('%6.2fs ⊘ %s aborted', t, ref)
                    result = SchedulerTasksStatus.abort
                    finish = True
                    self.aborting_tasks.remove(job_id)
                    self.jobs_failed += 1
                elif self.retry_jobs and isinstance(e, (asyncio.CancelledError, RetryJob)):
                    logger.info('%6.2fs ↻ %s cancelled, will be run again', t, ref)
                    self.jobs_retried += 1
                else:
                    logger.exception(
                        '%6.2fs ! %s failed, %s: %s', t, ref, e.__class__.__name__, e, extra={'extra': exc_extra}
                    )
                    result = SchedulerTasksStatus.failed
                    finish = True
                    self.jobs_failed += 1
            else:
                if hasattr(function, 'next_run'):
                    success = True
                else:
                    result = SchedulerTasksStatus.failed if result in [False, SchedulerTasksStatus.failed] \
                        else SchedulerTasksStatus.complete
                    success = SchedulerTasksStatus.complete == result
                finished_ms = timestamp_ms()
                logger.info('%6.2fs ← %s ● %s', (finished_ms - start_ms) / 1000, ref, result_str)
                finish = True
                self.jobs_complete += 1

            keep_result_forever = (
                self.keep_result_forever if function.keep_result_forever is None else function.keep_result_forever
            )
            result_timeout_s = self.keep_result_s if function.keep_result_s is None else function.keep_result_s
            result_data = None
            if result is not no_result and (keep_result_forever or result_timeout_s > 0):
                result_data = serialize_result(
                    function_name,
                    args,
                    kwargs,
                    job_try,
                    enqueue_time_ms,
                    success,
                    result,
                    start_ms,
                    finished_ms,
                    ref,
                    self.queue_name,
                    serializer=self.job_serializer,
                )

            if self.on_job_end:
                await self.on_job_end(ctx)

            await asyncio.shield(
                self.finish_job(
                    job_id,
                    finish,
                    result_data,
                    result_timeout_s,
                    keep_result_forever,
                    incr_score,
                    keep_in_progress,
                )
            )

            if self.after_job_end:
                await self.after_job_end(ctx)

    async def start_jobs(self, job_ids: List[bytes]) -> None:
        """
        For each job id, get the job definition, check it's not running and start it in a task
        """
        for job_id_b in job_ids:
            await self.sem.acquire()
            job_id = job_id_b.decode()
            in_progress_key = in_progress_key_prefix + job_id
            async with self.pool.pipeline(transaction=True) as pipe:
                await pipe.watch(in_progress_key)
                ongoing_exists = await pipe.exists(in_progress_key)
                score = await pipe.zscore(self.queue_name, job_id)
                if ongoing_exists or not score:
                    # job already started elsewhere, or already finished and removed from queue
                    self.sem.release()
                    logger.debug('job %s already running elsewhere', job_id)
                    continue

                try:
                    job_def: JobDef = await context.pool._get_job_def(job_id_b, None)
                    job_name = self.get_job_name(job_def.function)
                except Exception:
                    job_name = ''

                pipe.multi()
                pipe.psetex(
                    in_progress_key, int(self.in_progress_timeout_s * 1000), job_name.encode()
                )
                try:
                    await pipe.execute()
                except (ResponseError, WatchError):
                    # job already started elsewhere since we got 'existing'
                    self.sem.release()
                    logger.debug('multi-exec error, job %s already started elsewhere', job_id)
                else:
                    t = self.loop.create_task(self.run_job(job_id, int(score)))
                    t.add_done_callback(lambda _: self.sem.release())
                    self.tasks[job_id] = t
