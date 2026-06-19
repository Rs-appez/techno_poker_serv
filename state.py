import socketio

from models import Table


sio = socketio.AsyncServer(async_mode="asgi")

clients = {}
tables: dict[int, Table] = {}
