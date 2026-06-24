from socketio import AsyncServer

from decorators.permissions import is_current_player, is_host, require_auth, in_table
from models import Player, Table
from models.emiter import Emitter
from models.events import ClientEvent


class GameManager:
    def __init__(
        self,
        sio: AsyncServer,
        emitter: Emitter,
        clients: dict[str, str],
        tables: dict[int, Table],
    ):
        self.sio = sio
        self.clients = clients
        self.tables = tables
        self.emit = emitter
        self._register_events()

    def _register_events(self):
        auth = require_auth(self.sio, self.clients)
        host = is_host(self.sio)
        table = in_table(self.sio, self.tables)
        current_player = is_current_player(self.sio)

        @self.sio.on(ClientEvent.START_GAME.value)
        @auth
        @table
        @host
        async def start_game(sid, data, *, username, table: Table, **kwargs):
            try:
                table.start_game()
                await self.emit.game_started(table)
            except ValueError as e:
                await self.emit.error(sid, str(e))

        @self.sio.on(ClientEvent.BET.value)
        @auth
        @table
        @current_player
        async def bet(sid, data, *, player: Player, table: Table, **kwargs):
            amount = data.get("amount")
            if amount is None:
                await self.emit.error(sid, "Bet amount is required.")
                return

            try:
                table.place_bet(player, amount)
                await self.emit.player_action(ClientEvent.BET, table, player, amount)

            except ValueError as e:
                await self.emit.error(sid, str(e))

        @self.sio.on(ClientEvent.FOLD.value)
        @auth
        @table
        @current_player
        async def fold(sid, data, *, player: Player, table: Table, **kwargs):
            try:
                table.fold(player)
                await self.emit.player_action(ClientEvent.FOLD, table, player)
            except ValueError as e:
                await self.emit.error(sid, str(e))

        @self.sio.on(ClientEvent.CALL.value)
        @auth
        @table
        @current_player
        async def call(sid, data, *, player: Player, table: Table, **kwargs):
            try:
                amount_to_call = table.call(player)
                await self.emit.player_action(
                    ClientEvent.CALL, table, player, amount_to_call
                )

            except ValueError as e:
                await self.emit.error(sid, str(e))
