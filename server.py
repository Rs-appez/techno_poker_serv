import uvicorn

from models import LobbyManager

lobbyManager = LobbyManager()
app = lobbyManager.app

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=4587)
