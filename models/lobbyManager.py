from decorators.permissions import require_auth, require_table
from models import GameManager, Table, Player
import socketio


class LobbyManager:
    def __init__(self):
        self.sio = socketio.AsyncServer(async_mode="asgi")
        self.app = socketio.ASGIApp(self.sio)
        self.clients: dict[str, str] = {}
        self.tables: dict[int, Table] = {}
        self._register_events()
        self.game_manager = GameManager(self.sio, self.clients, self.tables)

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

        @self.sio.on("create_table")
        @auth
        async def create_table(sid, *, username, **kwargs):
            player = Player(name=username, sid=sid)
            new_table = Table(player)
            self.tables[new_table.id] = new_table
            await self.sio.emit("table_created", {"table_id": new_table.id}, room=sid)

        @self.sio.on("join_table")
        @auth
        @table
        async def join_table(sid, data, *, username, table, **kwargs):
            player = Player(name=username, sid=sid)
            table.add_player(player)
            await self.sio.emit("joined_table", {"table_id": table.id}, room=sid)
