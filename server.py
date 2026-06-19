import socketio
import uvicorn

from decorators.sockets_decorators import require_auth, require_table
from models import Player, Table
from state import clients, sio, tables

app = socketio.ASGIApp(sio)


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
@require_auth
async def create_table(sid, *, username, **kwargs):
    player = Player(name=username, sid=sid)
    new_table = Table(player)
    tables[new_table.id] = new_table
    await sio.emit("table_created", {"table_id": new_table.id}, room=sid)


@sio.on("join_table")
@require_auth
@require_table
async def join_table(sid, data, *, username, table, **kwargs):
    player = Player(name=username, sid=sid)
    table.add_player(player)
    await sio.emit("joined_table", {"table_id": table.id}, room=sid)


@sio.on("start_game")
@require_auth
@require_table
async def start_game(sid, data, *, username, table, **kwargs):
    if table.players[0].sid != sid:
        await sio.emit(
            "error", {"message": "Only the host can start the game."}, room=sid
        )
        return
    try:
        table.start_game()
        await sio.emit("game_started", {"table_id": table.id}, room=sid)
    except ValueError as e:
        await sio.emit("error", {"message": str(e)}, room=sid)


if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=4587)
