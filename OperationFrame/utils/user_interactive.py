# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2022/07/21
"""
import datetime
import typing as t

from OperationFrame.utils.cbvmenu import TAG_SAW
from OperationFrame.utils.context import context


def ask_input(msg: str, req: t.Literal['str', 'list'] = 'str', checkbox=None) -> t.Union[str, list]:
    """
    获取用户输入
    """
    formatted_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if checkbox is not None:
        _msg = f"\033[34m[{formatted_time}]\033[0m | \033[32mINPUT\033[0m   | {msg} <cb:{checkbox}>:"
    else:
        _msg = f"\033[34m[{formatted_time}]\033[0m | \033[32mINPUT\033[0m   | {msg}:"

    if req == 'list' and checkbox is not None:
        res = input(_msg).strip().split(checkbox)
        res = [x for x in res if x]
    else:
        res = input(_msg).strip()

    return res


def ask_yesno(msg: str) -> t.Optional[bool]:
    """
    获取用户输入回答，[y/n]
    """
    formatted_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if context.tag == TAG_SAW:
        return True

    while True:
        value = input(f"\033[34m[{formatted_time}]\033[0m | \033[32mYES/NO\033[0m  | {msg} [y/n]:").strip()
        return value.lower() == 'y'
