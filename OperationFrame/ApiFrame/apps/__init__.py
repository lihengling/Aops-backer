# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2023/04/07
"""
from OperationFrame.ApiFrame.apps.rbac.models import User, Role, Permission
from OperationFrame.ApiFrame.apps.asset.models import Department, Menu
from OperationFrame.ApiFrame.base.constant import ROUTER_SORT_DEFAULT, ROUTER_SORT_APP

# CBV 模型
MODEL_VIEWS = {
    # 业务 模型
    ROUTER_SORT_DEFAULT: [],
    # 用户、角色 模型
    ROUTER_SORT_APP: []
}
