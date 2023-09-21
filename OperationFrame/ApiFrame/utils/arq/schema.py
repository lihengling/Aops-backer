# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2023/06/29
"""
from typing import Any
from arq.constants import default_queue_name

from OperationFrame.utils.models import BaseModel
from OperationFrame.utils.scheduler_task import SchedulerTasksStatus


class JobStatus(BaseModel):
    job_id:        str
    job_name:      str
    job_params:    str
    start_time:  float
    finish_time: float = 0.0
    result:        Any = SchedulerTasksStatus.in_progress
    success:      bool = False
    queue_name:    str = default_queue_name
