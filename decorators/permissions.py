from functools import wraps


def require_auth(sio, clients):
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


def require_table(sio, tables):
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


def in_table(sio, tables):
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
