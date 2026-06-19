from socketio import AsyncServer

from decorators.permissions import is_current_player, is_host, require_auth, in_table
from models import Table


class GameManager:
    def __init__(
        self, sio: AsyncServer, clients: dict[str, str], tables: dict[int, Table]
    ):
        self.sio = sio
        self.clients = clients
        self.tables = tables
        self._register_events()

    def _register_events(self):
        auth = require_auth(self.sio, self.clients)
        host = is_host(self.sio)
        table = in_table(self.sio, self.tables)
        current_player = is_current_player(self.sio)

        @self.sio.on("start_game")
        @auth
        @table
        @host
        async def start_game(sid, data, *, username, table, **kwargs):
            try:
                table.start_game()
                await self.sio.emit("game_started", {"table_id": table.id}, room=sid)
            except ValueError as e:
                await self.sio.emit("error", {"message": str(e)}, room=sid)
