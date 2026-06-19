from uuid import UUID

import socketio
import uvicorn
from datetime import datetime

from models import Player, Table


sio = socketio.AsyncServer(async_mode="asgi")
app = socketio.ASGIApp(sio)

clients = {}
tables: dict[int, Table] = {}


@sio.event
async def connect(sid, environ, auth):
    username = auth.get("username")
    print(f"Client connected: {sid}, username: {username}")
    clients[sid] = username


@sio.event
async def disconnect(sid):
    username = clients.get(sid, "Unknown")
    print(f"Client disconnected: {sid}, username: {username}")
    clients.pop(sid, None)


# custom events
@sio.on("create_table")
async def create_table(sid):
    username = clients.get(sid, None)
    if not username:
        await sio.emit("error", {"message": "User not authenticated."}, room=sid)
        return
    player = Player(name=username, sid=sid)
    # Create a new table with the provided data
    new_table = Table(player)
    tables[new_table.id] = new_table

    # Emit the table ID back to the client
    await sio.emit("table_created", {"table_id": new_table.id}, room=sid)


@sio.on("join_table")
async def join_table(sid, data):
    username = clients.get(sid, None)
    if not username:
        await sio.emit("error", {"message": "User not authenticated."}, room=sid)
        return

    table_id = data.get("table_id")
    if table_id is None:
        await sio.emit("error", {"message": "Table ID is required."}, room=sid)
        return

    table = tables.get(table_id)
    if not table:
        await sio.emit("error", {"message": "Table not found."}, room=sid)
        return

    player = Player(name=username, sid=sid)
    table.add_player(player)

    # Emit a success message back to the client
    await sio.emit("joined_table", {"table_id": table.id}, room=sid)


if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=4587)
