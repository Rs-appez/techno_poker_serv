import socketio
import uvicorn
from datetime import datetime


sio = socketio.AsyncServer(async_mode="asgi")
app = socketio.ASGIApp(sio)

clients = {}


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
@sio.on("send_message")
async def send_message(sid, data):
    username = clients.get(sid, "Unknown")
    await sio.emit(
        "new_message",
        data
        | {"username": username, "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
    )


if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=4587)
