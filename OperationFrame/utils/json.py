# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2023/03/09
"""
from typing import *
import orjson
import pydantic.json
from dataclasses import is_dataclass, asdict


DEFAULT_ENCODERS_BY_TYPE: Dict[Type[Any], Callable[[Any], Any]] = {
    **pydantic.json.ENCODERS_BY_TYPE,
    set: lambda obj: list(obj),
    bytes: lambda obj: obj.decode('utf-8'),
}


def encoder(obj: Any) -> Any:
    """
    pydantic_encoder 所使用的 except KeyError 某些情况下会导致序列化方法中真正的 KeyError 无法正确抛出
    """
    if is_dataclass(obj):
        return asdict(obj)

    for base in obj.__class__.__mro__[:-1]:
        if base in DEFAULT_ENCODERS_BY_TYPE:
            return DEFAULT_ENCODERS_BY_TYPE[base](obj)
    else:
        raise TypeError(f"Object of type '{obj.__class__.__name__}' is not JSON serializable")


def dumps(obj: Any, *, option: int = 0, decode=True, default=None, **kwargs) -> Union[bytes, str]:
    json = orjson.dumps(obj, default=default or encoder, option=option)
    return json.decode('utf-8') if decode else json


loads = orjson.loads
