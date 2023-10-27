# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2023/03/21
"""
import jwt
from fastapi import Depends, Request
from fastapi.security import SecurityScopes
from datetime import timedelta, datetime

from jwt import PyJWTError
from pydantic import ValidationError

from OperationFrame.ApiFrame.apps.user.models import User
from OperationFrame.ApiFrame.base import constant
from OperationFrame.ApiFrame.base.exceptions import AccessTokenExpire, ForbiddenError
from OperationFrame.ApiFrame.base.security import OAuth2PasswordBearer

OAuth2 = OAuth2PasswordBearer('user/token', scheme_name="User", scopes={'is_admin': '管理员'})


def create_token(data: dict):
    """
    创建token
    """
    token_data = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=constant.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    token_data.update({"exp": expire})
    return jwt.encode(token_data, constant.JWT_SECRET_KEY, algorithm=constant.JWT_ALGORITHM)


async def check_permissions(req: Request, sec: SecurityScopes, token=Depends(OAuth2)):
    """
    权限验证
    """
    try:
        payload = jwt.decode(token, constant.JWT_SECRET_KEY, algorithms=[constant.JWT_ALGORITHM])
        username = payload.get('username', None)
        password = payload.get('password', None)
        if not payload or username is None or password is None:
            raise AccessTokenExpire

    except (PyJWTError, ValidationError, jwt.InvalidTokenError, jwt.ExpiredSignatureError) as err:
        msg = '凭证过期' if isinstance(err, jwt.ExpiredSignatureError) else AccessTokenExpire.message
        raise AccessTokenExpire(message=msg)

    # 检查用户
    user = await User().get_or_none(username=username)
    if not user or user.is_active is False:
        raise AccessTokenExpire(message='用户不存在或被禁用')

    # 检查权限
    if sec.scopes:
        if not await user.is_admin and sec.scopes:
            if not (set(sec.scopes) & await user.permission):
                raise ForbiddenError

    # 缓存用户信息
    req.state.user_id = user.id
    req.state.username = user.username
