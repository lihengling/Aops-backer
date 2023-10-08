# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2023/04/07
"""
from OperationFrame.ApiFrame.apps.auth.models import User, Role, Permission
from OperationFrame.ApiFrame.base.constant import ROUTER_SORT_DEFAULT, ROUTER_SORT_APP
from OperationFrame.models import Game

# CBV 模型
CBV_MODELS = {
    # 业务 模型
    ROUTER_SORT_DEFAULT: [Game],
    # 用户、角色 模型
    ROUTER_SORT_APP: [User, Role, Permission]
}
