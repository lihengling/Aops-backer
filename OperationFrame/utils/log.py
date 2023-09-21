# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2022/07/29
"""
import sys
from loguru import _defaults, logger as logger_uru
from loguru._logger import Logger as BaseLogger, Core

from OperationFrame.utils.context import context
from OperationFrame.utils.json import dumps
from OperationFrame.config import config

TAG_SAW = None
COLORIZE = True
FORMAT_TO_JSON = False

_defaults.LOGURU_INFO_COLOR = ""
_defaults.LOGURU_ERROR_COLOR = "<red><bold>"
_defaults.LOGURU_WARNING_COLOR = "<yellow><bold>"
_defaults.LOGURU_CRITICAL_COLOR = "<red><bold>"

EXTRA = " | <yellow>{extra}</yellow>"

DEBUG_MSG = "<blue>[{time:YYYY-MM-DD HH:mm:ss}]</blue> | " \
          "<green><level>{level:<7}</level></green> | " \
          "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | " \
          "<level>{message}</level>"

INFO_MSG = "<blue>[{time:YYYY-MM-DD HH:mm:ss}]</blue> | " \
            "<green><level>{level:<7}</level></green> | " \
            "<level>{message}</level>"


def formatter(record):
    global TAG_SAW
    if not TAG_SAW:
        from OperationFrame.utils.cbvmenu import TAG_SAW

    if record["level"].name in ['INFO', 'WARNING']:
        MSG = INFO_MSG
    else:
        MSG = DEBUG_MSG

    if record["extra"] and context.tag == TAG_SAW:
        if FORMAT_TO_JSON and isinstance(record["extra"], (list, dict)):
            record["extra"] = dumps(record["extra"])

    return f"{MSG}\n"


def formatter_request_file(record):
    msg = formatter(record).rstrip('\n')
    return f"{msg}{EXTRA} | {config.ENV}\n"


def filter_request_file(record):
    return record["extra"].get("Ts-Request-Id", None) is not None and 'http://' in record['message']


class Logger(BaseLogger):
    def add_request(self) -> None:
        self.add(config.LOGS_DIR_NAME + "/server-{time:YYYYMMDD}.log", colorize=COLORIZE,
                 level='DEBUG', format=formatter_request_file, filter=filter_request_file,
                 retention=f"{config.LOGS_ACCESS_SAVE} days", rotation="00:00")
        logger_uru.add(config.LOGS_DIR_NAME + "/error-{time:YYYYMMDD}.log", colorize=COLORIZE,
                       level='DEBUG', retention=f"{config.LOGS_ACCESS_SAVE} days", rotation="00:00")

    def add_task_file(self, file: str) -> int:
        filter_var = "_".join(file.split("/")[-1].split('_')[:-1])
        return self.add(
            file, format=formatter, level='DEBUG', colorize=COLORIZE,
            filter=lambda x: x['extra'].get('context', None) == filter_var and not x['extra'].get('task', None)
        )

    def add_worker_file(self, file: str, job_id: str = None) -> int:
        def _filter_worker_job(x):
            if job_id is not None:
                return bool(x["extra"].get('context', None)) == bool(x["extra"].get('task', None)) and \
                       x["extra"].get('job_id', "") == job_id
            else:
                return bool(x["extra"].get('context', None)) == bool(x["extra"].get('task', None))
        return self.add(file, level='DEBUG', colorize=COLORIZE, format=formatter, filter=_filter_worker_job)


logger = Logger(Core(), None, 0, False, False, False, False, True, None, {})
logger.add(config.LOGS_SUMMARY_DIR + '/summary-{time:YYYYMMDD}.log', format=formatter, level='WARNING',
           colorize=COLORIZE, retention=f"{config.LOGS_ACCESS_SAVE} days", rotation="00:00")
logger.add(sys.stdout, level='DEBUG', format=formatter, catch=False,
           filter=lambda x: bool(x["extra"].get('context', None)) == bool(x["extra"].get('task', None)) and x[
               'level'].name not in ['ERROR', 'CRITICAL'])
logger.add(sys.stdout,
           level='ERROR', format=DEBUG_MSG, catch=True,
           filter=lambda x: bool(x["extra"].get('context', None)) == bool(x["extra"].get('task', None)) and x[
               'level'].name in ['ERROR', 'CRITICAL'])
