from functools import wraps

from socketio import AsyncServer

from models import Table


def require_auth(sio: AsyncServer, clients: dict[str, str]):
    def decorator(handler):
        @wraps(handler)
        async def wrapper(sid, *args, **kwargs):
            username = clients.get(sid)
            if not username:
                await sio.emit("error", {"message": "Unauthorized"}, room=sid)
                return
            return await handler(sid, *args, username=username, **kwargs)

        return wrapper

    return decorator


def require_table(sio: AsyncServer, tables: dict[str, Table]):
    def decorator(handler):
        @wraps(handler)
        async def wrapper(sid, data, *args, **kwargs):
            table_id = data.get("table_id") if data else None
            table = tables.get(table_id)
            if not table:
                await sio.emit("error", {"message": "Table not found"}, room=sid)
                return
            return await handler(sid, data, *args, table=table, **kwargs)

        return wrapper

    return decorator


def in_table(sio: AsyncServer, tables: dict[int, Table]):
    def decorator(handler):
        @wraps(handler)
        async def wrapper(sid, data, *args, **kwargs):
            table_id = data.get("table_id") if data else None
            table = tables.get(table_id)
            if not table:
                await sio.emit("error", {"message": "Table not found"}, room=sid)
                return
            if not any(player.sid == sid for player in table.players):
                await sio.emit(
                    "error", {"message": "You must be a player at the table"}, room=sid
                )
                return
            return await handler(sid, data, *args, table=table, **kwargs)

        return wrapper

    return decorator


def is_host(sio: AsyncServer):
    def decorator(handler):
        @wraps(handler)
        async def wrapper(sid, data, *args, table: Table, **kwargs):
            if table.host_player.sid != sid:
                await sio.emit(
                    "error",
                    {"message": "Only the host can perform this action"},
                    room=sid,
                )
                return
            return await handler(sid, data, *args, table=table, **kwargs)

        return wrapper

    return decorator


def is_current_player(sio: AsyncServer):
    def decorator(handler):
        @wraps(handler)
        async def wrapper(sid, data, *args, table: Table, **kwargs):
            current_player = table.current_player
            if not current_player or current_player.sid != sid:
                await sio.emit(
                    "error",
                    {"message": "It's not your turn to play"},
                    room=sid,
                )
                return
            return await handler(
                sid, data, *args, player=current_player, table=table, **kwargs
            )

        return wrapper

    return decorator
