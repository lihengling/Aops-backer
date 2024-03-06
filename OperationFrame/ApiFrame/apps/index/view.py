# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2023/03/03
"""
from typing import Union, List, Any
from pydantic import BaseModel
from typing_extensions import Annotated

from fastapi import Query, Path, BackgroundTasks

from OperationFrame.ApiFrame.base import router_index


class UserIn(BaseModel):
    username: str
    password: str
    email: str
    full_name: Union[str, None] = None


class UserOut(BaseModel):
    username: str
    email: str
    full_name: Union[str, None] = None


@router_index.post("/user11/", response_model=UserOut)
async def create_user(user: UserIn) -> Any:
    return user