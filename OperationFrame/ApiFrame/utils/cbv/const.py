# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2023/03/21
"""

CBV_API_ROUTE = '__api_route__'

META_DEFAULT = '__meta_default__'
META_ANNOTATION = '__meta_annotation__'
META_RETURN_TYPE = '__meta_return_type__'
META_FIELDS = '__meta_fields__'
META_AUTO_MODEL = '__meta_auto_model__'
META_NOT_IMPLEMENTED = '__meta_not_implemented__'

QUERYSET_AUTO_MODEL = '__queryset_auto_model__'
QUERYSET_AUTO_MODEL_KEY = 'AutoModeMeta'
QUERYSET_AUTO_MODEL_READONLY = '__queryset_auto_model_readonly__'
QUERYSET_AUTO_MODEL_READONLY_KEY = 'AutoModeReadonlyMeta'

METHOD_FUNCTIONS = {
    '_post': 'POST',
    '_post_list': 'POST',
    '_delete': 'DELETE',
    '_delete_list': 'DELETE',
    '_put': 'PUT',
    '_put_list': 'PUT',
    '_get': 'GET',
    '_get_list': 'GET',
}

ID_PATH = ['_post', '_delete', '_put', '_get']

PYDANTIC_META_KEYS = ['exclude', 'include', 'computed', 'optional']

LIMIT = 20
OFFSET = 0
