# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2022/07/20
"""
from OperationFrame.menu_logics.game.logics_control_status import start
from OperationFrame.utils.cbvmenu import GameCbv
from OperationFrame.utils.cbvmenu import TYPE_WORKER
from OperationFrame.utils.cbvmenu.model import MetaRoute
from OperationFrame.utils.models import BaseResponse, JobResponse


class GameStart(GameCbv):

    class Meta:
        name = '游戏服 启动'
        sign = 'game_start'
        func = start
        log = True
        route = MetaRoute(**{
            'name': name,
            'path': '/game/game_start',
            'tags': ['Game', TYPE_WORKER],
            'methods': ['GET'],
            'response_model': BaseResponse[JobResponse]
        })
