# WebSocket Chat Demo (FastAPI)

A minimal room-based chat server built with FastAPI's native WebSocket
support. Any number of clients can join the same room and chat together —
including a mix of the bundled HTML/JS web client and the Python CLI
client.

## How it works

- `server.py` exposes one endpoint: `ws://<host>/ws/{room}/{username}`.
- All connections that share the same `{room}` value are grouped together
  by an in-memory `RoomManager` and messages are broadcast to everyone in
  that room.
- `static/index.html` is a browser client served at `/`.
- `python_client.py` is a terminal client using the `websockets` library.

Because both clients talk to the same endpoint and the same room concept,
a browser user and a Python-client user typing the same room name land in
the same conversation.

## Run locally

```bash
pip install -r requirements.txt
uvicorn server:app --reload
```

Open http://localhost:8000 in a browser, enter a name and room (e.g.
`general`), and join.

In another terminal, connect the Python client to the same room:

```bash
python python_client.py --host localhost:8000 --room general --username alice
```

Messages sent from either client appear in both.

## Deploy to Render

1. Push this project to a GitHub repo.
2. In Render, choose **New > Web Service**, connect the repo, and Render
   will pick up `render.yaml` automatically (or set manually):
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn server:app --host 0.0.0.0 --port $PORT`
3. Deploy. Render gives you a URL like `https://websocket-demo-chat.onrender.com`.

Render terminates TLS for you, so WebSocket connections must use `wss://`.

## Connect to the deployed app

**Browser:** open `https://<your-app>.onrender.com/` — it already uses
`wss://` automatically when served over HTTPS.

**Python client:**

```bash
python python_client.py --host <your-app>.onrender.com --secure --room general --username bob
```

## Notes

- Room membership and message history are kept in memory only — restarting
  the server (or Render spinning down an idle free-tier instance) clears
  all rooms.
- This demo has no authentication; usernames are just display labels
  supplied by the client.
