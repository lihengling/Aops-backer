# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2023/03/21
"""
import datetime

# jwt 常量
JWT_TOKEN_MAX_AGE:           datetime = datetime.timedelta(days=1)
JWT_SECRET_KEY:                   str = "09d25e094faa6ca2556c818166b7"
JWT_ALGORITHM:                    str = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES:  int = 24 * 60
JWT_TOKEN_TYPE:                   str = 'bearer'

# 路由分类
ROUTER_SORT_APP:                  str = 'app'
ROUTER_SORT_DEFAULT:              str = 'default'
ROUTER_START_SWITCH:              str = '/api'

# 接口权限标识
PERMISSION_INFO:                 str = 'info'
PERMISSION_UPDATE:               str = 'update'
PERMISSION_DELETE:               str = 'delete'

# 模糊匹配字段(以列表形式定义在 Meta 中)
QUERY_FIELDS:                    str = 'query_fields'
