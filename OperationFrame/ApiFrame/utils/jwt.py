# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2023/03/21
"""
import jwt
from datetime import timedelta, datetime

from OperationFrame.ApiFrame.base import constant


def create_token(data: dict):
    token_data = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=constant.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    token_data.update({"exp": expire})
    return jwt.encode(token_data, constant.JWT_SECRET_KEY, algorithm=constant.JWT_ALGORITHM)
