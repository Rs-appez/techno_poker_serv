from decorators.permissions import require_auth, require_table
from models import Emitter, GameManager, Table, Player
import socketio

from models.events import ClientEvent


class LobbyManager:
    def __init__(self):
        self.sio = socketio.AsyncServer(async_mode="asgi")
        self.app = socketio.ASGIApp(self.sio)
        self.clients: dict[str, str] = {}
        self.tables: dict[int, Table] = {}
        self.emit = Emitter(self.sio)
        self._register_events()
        self.game_manager = GameManager(self.sio, self.emit, self.clients, self.tables)

    def _register_events(self):
        auth = require_auth(self.sio, self.clients)
        table = require_table(self.sio, self.tables)

        @self.sio.event
        async def connect(sid, environ, auth_data):
            username = auth_data.get("username")
            print(f"Client connected: {sid}, username: {username}")
            self.clients[sid] = username

        @self.sio.event
        @auth
        async def disconnect(sid):
            username = self.clients.get(sid)
            print(f"Client disconnected: {sid}, username: {username}")
            self.clients.pop(sid)

        @self.sio.on(ClientEvent.LIST_TABLES.value)
        @auth
        async def list_tables(sid, *, username, **kwargs):
            tables_info = [
                {
                    "table_id": table.id,
                    "num_players": len(table.players),
                    "host_name": table.players[0].name,
                }
                for table in self.tables.values()
                if not table.has_started
            ]
            return {"tables": tables_info}

        @self.sio.on(ClientEvent.CREATE_TABLE.value)
        @auth
        async def create_table(sid, *, username, **kwargs):
            player = Player(name=username, sid=sid)
            new_table = Table(player)
            self.tables[new_table.id] = new_table
            await self.sio.enter_room(sid, f"table_{new_table.id}")
            return {"table_id": new_table.id, "num_players": 1, "host_name": username}

        @self.sio.on(ClientEvent.JOIN_TABLE.value)
        @auth
        @table
        async def join_table(sid, data, *, username, table, **kwargs):
            player = Player(name=username, sid=sid)
            table.add_player(player)
            await self.sio.enter_room(sid, f"table_{table.id}")
            await self.emit.joined_table(player, table)
