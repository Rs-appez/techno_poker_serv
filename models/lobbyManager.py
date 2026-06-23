from decorators.permissions import require_auth, require_table
from models import Emitter, GameManager, Table, Player
import socketio

from models.emitModels import EmitTable
from models.events import ClientEvent


class LobbyManager:
    def __init__(self):
        self.sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
        self.app = socketio.ASGIApp(self.sio, socketio_path="socket.io/")
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
        async def disconnect(sid):
            username = self.clients.get(sid)
            print(f"Client disconnected: {sid}, username: {username}")
            _ = self.clients.pop(sid)
            tables_to_remove = []
            for table in self.tables.values():
                player = next((p for p in table.players if p.sid == sid), None)
                if player:
                    table.remove_player(player)
                    await self.sio.leave_room(sid, table.room)
                    if table.host_player.sid == sid:
                        if table.players:
                            table.host_player = table.players[0]
                        else:
                            tables_to_remove.append(table.id)

                    _ = await self.emit.joined_table(player, table, is_joining=False)

            for table_id in tables_to_remove:
                del self.tables[table_id]

        @self.sio.on(ClientEvent.LIST_TABLES.value)
        @auth
        async def list_tables(sid, *, username, **kwargs):
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
                self.tables[new_table.id] = new_table
                await self.sio.enter_room(sid, new_table.room)
                return EmitTable.from_table(new_table).to_dict()
            except Exception as e:
                await self.emit.error(sid, f"Error while creating table: {str(e)}")
                return {"error": str(e)}

        @self.sio.on(ClientEvent.JOIN_TABLE.value)
        @auth
        @table
        async def join_table(sid, data, *, username, table, **kwargs):
            try:
                player = Player(name=username, sid=sid)
                table.add_player(player)
                await self.sio.enter_room(sid, table.room)
                return await self.emit.joined_table(player, table)
            except Exception as e:
                await self.emit.error(sid, f"Error while joining table: {str(e)}")

        @self.sio.on(ClientEvent.QUIT_TABLE.value)
        @auth
        @table
        async def quit_table(sid, data, *, username, table: Table, **kwargs):
            try:
                player = next((p for p in table.players if p.sid == sid), None)
                if player:
                    table.remove_player(player)
                    await self.sio.leave_room(sid, table.room)
                    _ = await self.emit.joined_table(player, table, is_joining=False)
            except Exception as e:
                await self.emit.error(sid, f"Error while quitting table: {str(e)}")
