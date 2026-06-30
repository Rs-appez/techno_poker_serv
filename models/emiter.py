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
        self,
        new_player: Player,
        table: Table,
        is_joining: bool = True,
        is_silent: bool = False,
    ):
        emit_player = EmitPlayer.from_player(new_player)
        emit_table = EmitTable.from_table(table)
        emit_change_table = EmitChangeTable(
            emit_player, is_joining, table.host_player.name
        )
        if not is_silent:
            await self.sio.emit(
                ServerEvent.JOINED_TABLE, emit_change_table.to_dict(), room=table.room
            )

        emit_new_player = EmitPlayer.from_player(new_player, show_hand=True)
        emit_table.players = [
            p if p.player_name != new_player.name else emit_new_player
            for p in emit_table.players
        ]
        return emit_table.to_dict()

    async def game_started(self, table: Table):
        for player in table.players:
            emit_table = EmitTable.from_table(table, player_with_hand=player)
            await self.sio.emit(
                ServerEvent.GAME_STARTED, emit_table.to_dict(), room=player.sid
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
        for player in table.players:
            emit_table = EmitTable.from_table(table, player_with_hand=player)
            emit_player_action.table = emit_table
            await self.sio.emit(
                ServerEvent.PLAYER_ACTION, emit_player_action.to_dict(), room=player.sid
            )

    async def next_round(self, table: Table):
        for player in table.players:
            emit_table = EmitTable.from_table(table, player_with_hand=player)
            await self.sio.emit(
                ServerEvent.NEXT_ROUND, emit_table.to_dict(), room=player.sid
            )

    async def end_round(self, table: Table, emit_table_final: EmitTable):
        result = emit_table_final.to_dict()
        if table.round_winners:
            result.update(
                {
                    "winners": [
                        EmitPlayer.from_player(winner).to_dict()
                        for winner in table.round_winners
                    ]
                }
            )
        await self.sio.emit(ServerEvent.END_ROUND, result, room=table.room)

    async def end_game(self, table: Table, winner: Player):
        emit_winner = EmitPlayer.from_player(winner)
        await self.sio.emit(
            ServerEvent.END_GAME, emit_winner.to_dict(), room=table.room
        )
