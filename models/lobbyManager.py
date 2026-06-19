from functools import wraps
from models import Table, Player
import socketio


class LobbyManager:
    def __init__(self):
        self.sio = socketio.AsyncServer(async_mode="asgi")
        self.app = socketio.ASGIApp(self.sio)
        self.clients: dict[str, str] = {}
        self.tables: dict[int, Table] = {}
        self._register_events()

    def _require_auth(self, handler):
        @wraps(handler)
        async def wrapper(sid, *args, **kwargs):
            username = self.clients.get(sid)
            if not username:
                await self.sio.emit("error", {"message": "Unauthorized"}, room=sid)
                return
            return await handler(sid, *args, username=username, **kwargs)

        return wrapper

    def _require_table(self, handler):
        @wraps(handler)
        async def wrapper(sid, data, *args, **kwargs):
            table_id = data.get("table_id") if data else None
            table = self.tables.get(table_id)
            if not table:
                await self.sio.emit("error", {"message": "Table not found"}, room=sid)
                return
            return await handler(sid, data, *args, table=table, **kwargs)

        return wrapper

    def _register_events(self):
        @self.sio.event
        async def connect(sid, environ, auth):
            username = auth.get("username")
            print(f"Client connected: {sid}, username: {username}")
            self.clients[sid] = username

        @self.sio.event
        async def disconnect(sid):
            username = self.clients.get(sid, "Unknown")
            print(f"Client disconnected: {sid}, username: {username}")
            self.clients.pop(sid, None)

        @self.sio.on("create_table")
        @self._require_auth
        async def create_table(sid, *, username, **kwargs):
            player = Player(name=username, sid=sid)
            new_table = Table(player)
            self.tables[new_table.id] = new_table
            await self.sio.emit("table_created", {"table_id": new_table.id}, room=sid)

        @self.sio.on("join_table")
        @self._require_auth
        @self._require_table
        async def join_table(sid, data, *, username, table, **kwargs):
            player = Player(name=username, sid=sid)
            table.add_player(player)
            await self.sio.emit("joined_table", {"table_id": table.id}, room=sid)

        @self.sio.on("start_game")
        @self._require_auth
        @self._require_table
        async def start_game(sid, data, *, username, table, **kwargs):
            if table.players[0].sid != sid:
                await self.sio.emit(
                    "error", {"message": "Only the host can start the game."}, room=sid
                )
                return
            try:
                table.start_game()
                await self.sio.emit("game_started", {"table_id": table.id}, room=sid)
            except ValueError as e:
                await self.sio.emit("error", {"message": str(e)}, room=sid)
