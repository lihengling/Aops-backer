# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2023/10/08
"""
from typing import Optional

from fastapi.security.utils import get_authorization_scheme_param
from starlette.requests import Request

from fastapi.security import OAuth2PasswordBearer as BaseOAuth2PasswordBearer, \
    OAuth2AuthorizationCodeBearer as BaseOAuth2AuthorizationCodeBearer, OAuth2

from OperationFrame.ApiFrame.base.exceptions import AccessTokenExpire


AUTH_HEADER = 'Authorization'
AUTH_SCHEME = 'bearer'


class OAuth2Bearer(OAuth2):
    async def __call__(self, request: Request) -> Optional[str]:
        authorization: str = request.headers.get(AUTH_HEADER)
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != AUTH_SCHEME:
            if self.auto_error:
                raise AccessTokenExpire
            else:
                return None
        return param


class OAuth2PasswordBearer(OAuth2Bearer, BaseOAuth2PasswordBearer):
    ...


class OAuth2AuthorizationCodeBearer(OAuth2Bearer, BaseOAuth2AuthorizationCodeBearer):
    ...
