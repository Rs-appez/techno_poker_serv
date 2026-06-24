from socketio import AsyncServer
from models import Player, Table
from models.events import ClientEvent, ServerEvent
from models.emitModels import (
    EmitError,
    EmitChangeTable,
    EmitHand,
    EmitPlayer,
    EmitPlayerAction,
    EmitTable,
    EmitAuthToken,
)


class Emitter:
    def __init__(self, sio: AsyncServer):
        self.sio = sio

    async def error(self, room: str, error_msg: str):
        error = EmitError(message=error_msg)
        await self.sio.emit(ServerEvent.ERROR, error.to_dict(), room=room)

    async def auth_token(self, sid: str, token: str):
        auth_token = EmitAuthToken(token=token)
        await self.sio.emit(ServerEvent.AUTH_TOKEN, auth_token.to_dict(), room=sid)

    async def joined_table(
        self, new_player: Player, table: Table, is_joining: bool = True
    ):
        emit_player = EmitPlayer.from_player(new_player)
        emit_table = EmitTable.from_table(table)
        emit_change_table = EmitChangeTable(
            emit_player, is_joining, table.host_player.name
        )
        await self.sio.emit(
            ServerEvent.JOINED_TABLE, emit_change_table.to_dict(), room=table.room
        )

        emit_new_player = EmitPlayer.from_player(new_player, hide_hand=False)
        emit_table.players = [
            p if p.player_name != new_player.name else emit_new_player
            for p in emit_table.players
        ]
        return emit_table.to_dict()

    async def game_started(self, table: Table):
        emit_table = EmitTable.from_table(table)
        await self.sio.emit(
            ServerEvent.GAME_STARTED, emit_table.to_dict(), room=table.room
        )

    async def player_action(
        self,
        action: ClientEvent,
        table: Table,
        player: Player,
        amount: int | None = None,
    ):

        emit_player_action = EmitPlayerAction(
            action=action, table=table, player=player, amount=amount
        )
        await self.sio.emit(
            ServerEvent.PLAYER_ACTION, emit_player_action.to_dict(), room=table.room
        )

    async def hand_dealt(self, player: Player):
        emit_hand = EmitHand.from_player(player)
        await self.sio.emit(
            ServerEvent.CARDS_DEALT, emit_hand.to_dict(), room=player.sid
        )
