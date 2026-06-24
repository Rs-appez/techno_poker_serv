import asyncio
import uuid
from decorators.permissions import require_auth, require_table
from models import Emitter, GameManager, Table, Player
import socketio

from models.emitModels import EmitTable
from models.events import ClientEvent


class LobbyManager:
    def __init__(self):
        self.sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
        self.app = socketio.ASGIApp(self.sio, socketio_path="socket.io/")
        self.clients: dict[str, dict[str, str]] = {}
        self.players: set[Player] = set()
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
            token = auth_data.get("token")
            if token:
                if old_sid := next(
                    (s for s, u in self.clients.items() if u.get("token") == token),
                    None,
                ):
                    self._change_player_sid(old_sid, sid)
                print(f"Client reconnected: {sid}, username: {username}")
            else:
                token = uuid.uuid4().hex
                asyncio.create_task(self.emit.auth_token(sid, token))
                print(f"Client connected: {sid}, username: {username}")
            self.clients[sid] = {"username": username, "token": token}

        @self.sio.event
        async def disconnect(sid, *args, **kwargs):
            asyncio.create_task(self._disconnect_player(sid))

        @self.sio.on(ClientEvent.LIST_TABLES.value)
        @auth
        async def list_tables(sid, *args, **kwargs):
            tables_info = [
                EmitTable.from_table(table).to_dict()
                for table in self.tables.values()
                if not table.has_started
            ]
            return {"tables": tables_info}

        @self.sio.on(ClientEvent.CREATE_TABLE.value)
        @auth
        async def create_table(sid, *, username, **kwargs):
            try:
                player = Player(name=username, sid=sid)
                new_table = Table(player, emitter=self.emit)
                self.players.add(player)
                self.tables[new_table.id] = new_table
                await self.sio.enter_room(sid, new_table.room)
                return EmitTable.from_table(new_table).to_dict()
            except Exception as e:
                await self.emit.error(sid, f"Error while creating table: {str(e)}")
                return {"error": str(e)}

        @self.sio.on(ClientEvent.JOIN_TABLE.value)
        @auth
        @table
        async def join_table(sid, _, *, username: str, table: Table, **kwargs):
            player = next((p for p in table.players if p.sid == sid), None)
            if player:
                return await self.emit.joined_table(player, table)
            try:
                player = Player(name=username, sid=sid)
                self.players.add(player)
                table.add_player(player)
                await self.sio.enter_room(sid, table.room)
                return await self.emit.joined_table(player, table)
            except Exception as e:
                await self.emit.error(sid, f"Error while joining table: {str(e)}")

        @self.sio.on(ClientEvent.QUIT_TABLE.value)
        @auth
        @table
        async def quit_table(sid, _, *, table: Table, **kwargs):
            try:
                await self._remove_player_from_table(sid, table)
            except Exception as e:
                await self.emit.error(sid, f"Error while quitting table: {str(e)}")

    def _change_player_sid(self, old_sid: str, new_sid: str):
        del self.clients[old_sid]
        for player in [p for p in self.players if p.sid == old_sid]:
            player.sid = new_sid

    async def _remove_player_from_table(self, sid: str, table: Table):
        player = next((p for p in table.players if p.sid == sid), None)
        if player:
            table.remove_player(player)
            if table.host_player.sid == sid:
                if table.players:
                    table.host_player = table.players[0]
                    _ = await self.emit.joined_table(player, table, is_joining=False)
                else:
                    del self.tables[table.id]
            await self.sio.leave_room(sid, table.room)
            self.players.discard(player)

    async def _remove_player_from_all_tables(self, sid: str):
        _ = self.clients.pop(sid)
        for table in list(self.tables.values()):
            await self._remove_player_from_table(sid, table)

    async def _disconnect_player(self, sid: str, timeout: int = 60):
        username = self.clients.get(sid, {}).get("username")
        await asyncio.sleep(timeout)
        if sid in self.clients:
            print(f"Disconnecting player {username} due to inactivity.")
            await self._remove_player_from_all_tables(sid)
