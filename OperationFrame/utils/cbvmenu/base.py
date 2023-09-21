# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2022/07/21
"""
import asyncio
import typing as t
from inspect import signature

from .constant import TAG_U_MOUNTED, TAG_SAW, TAG_DB, TYPE_SERVICE, TYPE_FRAME
from .model import BaseMeta, MenuTask


def _get_attr(mcs, key) -> t.Any:
    meta: BaseMeta = getattr(mcs, 'Meta', None)
    return getattr(meta if hasattr(meta, key) else BaseMeta, key)


def _format_param(method: t.Union[t.Callable, t.Awaitable]) -> str:
    parameters = dict(signature(method).parameters)
    parameters_info = []
    for param in parameters:
        param_default = None
        try:
            if parameters[param].default.__name__ == '_empty':
                param_default = '_empty'
        except AttributeError:
            pass
        param_name = str(parameters[param])
        param_name = param_name.split('=')[0].split(':')[0]
        parameters_info.append(f'--{param_name}' if param_default is None else f'{param_name}')

    if len(parameters_info) == 0:
        parameters_info = None

    return str(parameters_info).replace("'", "").replace("[", "").replace("]", "")


class MenuMetaClass(type):
    def __new__(mcs, cls_name, bases, attrs):
        mcs = type.__new__(mcs, cls_name, bases, attrs)
        self = mcs()

        params:   str = _format_param(self.run)
        name:     str = _get_attr(mcs, 'name')
        sign:     str = _get_attr(mcs, 'sign')
        mounted: bool = _get_attr(mcs, 'mounted')
        d_mysql: bool = _get_attr(mcs, 'depend_mysql')
        d_redis: bool = _get_attr(mcs, 'depend_redis')
        route:   dict = _get_attr(mcs, 'route')
        log:     bool = _get_attr(mcs, 'log')
        tag:      str = TAG_U_MOUNTED if not mounted else _get_attr(mcs, 'tag')
        tag:      str = tag in [TAG_SAW, TAG_DB] \
                        and f'{TYPE_FRAME}-{tag}' or tag != TAG_U_MOUNTED and f'{TYPE_SERVICE}-{tag}' or tag

        if sign:
            task: MenuTask = MenuTask(**{
                'name': name, 'sign': sign, 'self': self,  'params': params, 'mounted': mounted,
                'depend_mysql': d_mysql, 'depend_redis': d_redis, 'tag': tag, 'route': route, 'log': log}
            )
            menu.tasks.setdefault(tag, list()).append(task)

        return mcs


class MenuManager:
    tasks: t.Dict[str, t.List[MenuTask]] = {}

    def __init__(
        self,
        on_startup: t.Sequence[t.Callable] = None,
        on_shutdown: t.Sequence[t.Callable] = None,
    ):
        self.on_startup = [] if on_startup is None else list(on_startup)
        self.on_shutdown = [] if on_shutdown is None else list(on_shutdown)
        self.lifespan_context: t.Callable = _DefaultLifespan(self)

    def __getitem__(self, item) -> t.Union[MenuTask, None]:
        for task in self.tasks.values():
            for task_obj in task:
                if task_obj.sign == item:
                    return task_obj

    def add_event_handler(self, event_type: str, func: t.Callable) -> None:
        assert event_type in ("startup", "shutdown")

        if event_type == "startup":
            self.on_startup.append(func)
        else:
            self.on_shutdown.append(func)

    def on_event(self, event_type: str) -> t.Callable:
        def decorator(func: t.Callable) -> t.Callable:
            self.add_event_handler(event_type, func)
            return func

        return decorator

    async def startup(self) -> None:
        for handler in self.on_startup:
            if asyncio.iscoroutinefunction(handler):
                await handler()
            else:
                handler()

    async def shutdown(self) -> None:
        for handler in self.on_shutdown:
            if asyncio.iscoroutinefunction(handler):
                await handler()
            else:
                handler()


class _DefaultLifespan:
    def __init__(self, manager: MenuManager):
        self.manager = manager

    async def __aenter__(self) -> None:
        await self.manager.startup()

    async def __aexit__(self, *exc_info: object) -> None:
        await self.manager.shutdown()

    def __call__(self: t.TypeVar) -> t.TypeVar:
        return self


menu = MenuManager()
