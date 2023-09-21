# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2023/05/19
"""
import typing as t
import time
from datetime import datetime


def timestampToTimeStr(ts: t.Union[str, int], time_output: str = '%Y-%m-%d %H:%M:%S') -> str:
    return datetime.fromtimestamp(int(ts)).strftime(time_output)


def timeStrToTimestamp(ts: str, time_input: str = '%Y-%m-%d %H:%M:%S') -> int:
    return int(time.mktime(time.strptime(ts, time_input)))
