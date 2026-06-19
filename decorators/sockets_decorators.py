from functools import wraps

from state import clients, sio, tables


def require_auth(f):
    @wraps(f)
    async def wrapper(sid, *args, **kwargs):
        username = clients.get(sid)
        if not username:
            await sio.emit("error", {"message": "User not authenticated."}, room=sid)
            return
        return await f(sid, *args, username=username, **kwargs)

    return wrapper


def require_table(f):
    @wraps(f)
    async def wrapper(sid, data, *args, **kwargs):
        table_id = data.get("table_id")
        if table_id is None:
            await sio.emit("error", {"message": "Table ID is required."}, room=sid)
            return
        table = tables.get(table_id)
        if not table:
            await sio.emit("error", {"message": "Table not found."}, room=sid)
            return
        return await f(sid, data, *args, table=table, **kwargs)

    return wrapper
