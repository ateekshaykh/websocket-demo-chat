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

## Deploy to EC2

**1. Launch an instance** (AWS Console → EC2 → Launch Instance)

- AMI: Ubuntu Server 24.04 LTS (or 22.04), free-tier eligible
- Instance type: `t2.micro` / `t3.micro`
- Key pair: create a new one, download the `.pem` file
- Security group inbound rules:
  - SSH (22) from "My IP"
  - Custom TCP, port `8000`, from Anywhere (0.0.0.0/0) — this serves the app
- Launch, then note the instance's **public IPv4 address**

**2. SSH in**

```bash
chmod 400 your-key.pem
ssh -i your-key.pem ubuntu@<EC2-public-ip>
```

**3. Deploy the app**

On the instance, download and run the setup script (it installs Python,
clones the repo, and runs the server as a systemd service that restarts
automatically):

```bash
curl -O https://raw.githubusercontent.com/ateekshaykh/websocket-demo-chat/main/deploy/ec2-setup.sh
chmod +x ec2-setup.sh
REPO_URL="https://github.com/ateekshaykh/websocket-demo-chat.git" ./ec2-setup.sh
```

If the repo is private, embed a [personal access token](https://github.com/settings/tokens)
in the URL instead: `REPO_URL="https://<token>@github.com/ateekshaykh/websocket-demo-chat.git"`.

Check it's running: `sudo systemctl status websocket-chat`, logs via
`sudo journalctl -u websocket-chat -f`.

**4. Connect**

The app is served over plain HTTP on port 8000, so both clients use `ws://` (not `wss://`):

- **Browser:** open `http://<EC2-public-ip>:8000/`
- **Python client:**
  ```bash
  python python_client.py --host <EC2-public-ip>:8000 --room general --username alice
  ```

To redeploy after pushing new code, re-run the same command on the instance
(`git pull` + service restart) — or just re-run `ec2-setup.sh` again, it's
safe to run repeatedly.

**Going further:** this setup uses the raw IP over plain HTTP/WS. For a
proper domain with `https://`/`wss://` (matching how the Render deployment
behaves), put Nginx in front as a reverse proxy and get a free cert with
Certbot/Let's Encrypt — ask if you want that added.

## Notes

- Room membership and message history are kept in memory only — restarting
  the server (or Render spinning down an idle free-tier instance) clears
  all rooms.
- This demo has no authentication; usernames are just display labels
  supplied by the client.
