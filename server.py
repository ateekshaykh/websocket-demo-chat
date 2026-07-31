"""
FastAPI WebSocket chat server with room support.

Clients connect to:  ws(s)://<host>/ws/{room}/{username}

Any number of clients can join the same room (identified by the {room}
path segment) regardless of whether they're using the HTML/JS client or
the Python client — messages are broadcast to every connection currently
in that room.
"""
import json
from datetime import datetime, timezone
from typing import Dict, Optional, Set

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="WebSocket Chat Demo")


class RoomManager:
    """Tracks active WebSocket connections grouped by room name."""

    def __init__(self) -> None:
        self.rooms: Dict[str, Set[WebSocket]] = {}

    async def connect(self, room: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self.rooms.setdefault(room, set()).add(websocket)

    def disconnect(self, room: str, websocket: WebSocket) -> None:
        connections = self.rooms.get(room)
        if not connections:
            return
        connections.discard(websocket)
        if not connections:
            self.rooms.pop(room, None)

    async def broadcast(self, room: str, message: dict, *, exclude: Optional[WebSocket] = None) -> None:
        connections = self.rooms.get(room, set())
        payload = json.dumps(message)
        dead: Set[WebSocket] = set()
        for connection in connections:
            if connection is exclude:
                continue
            try:
                await connection.send_text(payload)
            except Exception:
                dead.add(connection)
        for connection in dead:
            connections.discard(connection)

    def room_size(self, room: str) -> int:
        return len(self.rooms.get(room, set()))


manager = RoomManager()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.websocket("/ws/{room}/{username}")
async def websocket_endpoint(websocket: WebSocket, room: str, username: str) -> None:
    await manager.connect(room, websocket)
    await manager.broadcast(
        room,
        {
            "type": "system",
            "message": f"{username} joined the room",
            "room": room,
            "users_online": manager.room_size(room),
            "timestamp": _now(),
        },
    )

    try:
        while True:
            raw = await websocket.receive_text()

            # Accept either plain text or a JSON payload like {"message": "..."}
            try:
                data = json.loads(raw)
                text = data.get("message", "")
            except (json.JSONDecodeError, AttributeError):
                text = raw

            if not text:
                continue

            await manager.broadcast(
                room,
                {
                    "type": "message",
                    "username": username,
                    "message": text,
                    "room": room,
                    "timestamp": _now(),
                },
            )
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(room, websocket)
        await manager.broadcast(
            room,
            {
                "type": "system",
                "message": f"{username} left the room",
                "room": room,
                "users_online": manager.room_size(room),
                "timestamp": _now(),
            },
        )


# Serve the HTML/JS client at the site root and its static assets under /static.
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def index() -> HTMLResponse:
    with open("static/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())
