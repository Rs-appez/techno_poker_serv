from socketio import AsyncServer
from models import Player, Table
from models.events import ClientEvent, ServerEvent
from models.emitModels import (
    EmitError,
    EmitChangeTable,
    EmitPlayer,
    EmitMyplayer,
    EmitPlayerAction,
    EmitTable,
)


class Emitter:
    def __init__(self, sio: AsyncServer):
        self.sio = sio

    async def error(self, table: Table, error_msg: str):
        error = EmitError(message=error_msg)
        await self.sio.emit(ServerEvent.ERROR, error.to_dict(), room=table.room)

    async def joined_table(self, new_player: Player, table: Table):
        emit_player = EmitPlayer.from_player(new_player, table)
        emit_change_table = EmitChangeTable(emit_player, True)
        await self.sio.emit(
            ServerEvent.JOINED_TABLE, emit_change_table.to_dict(), room=table.room
        )

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
