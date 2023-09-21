# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2023/05/16
"""
from OperationFrame.utils.cbvmenu import GameCbv, TAG_SAW
from OperationFrame.utils.context import context
from OperationFrame.utils.models import BaseModel, BaseResponse
from OperationFrame.utils.user_interactive import ask_input


class GameInfoReq(BaseModel):
    srv_id:  str = None
    status:  str = None


class GameInfo(GameCbv):

    async def run(self, srv_id: str):
        srv_id = srv_id or (ask_input('输入srv_id') if context.tag != TAG_SAW else None)
        req: dict = {'srv_id': srv_id, 'status': 'up'}
        if context.tag != TAG_SAW:
            print(req)
        return BaseResponse[GameInfoReq](data=req)

    class Meta:
        name = '游戏服 详细信息'
        sign = 'game_info'
        route = {
            'name': name,
            'path': '/game/game_info',
            'tags': ['Game'],
            'methods': ['GET'],
            'response_model': BaseResponse[GameInfoReq]
        }
