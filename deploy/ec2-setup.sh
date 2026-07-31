#!/usr/bin/env bash
# Run this ON the EC2 instance (after SSH-ing in) to install, configure, and
# start the WebSocket chat server as a systemd service that survives reboots
# and restarts automatically if it crashes.
#
# Usage:
#   REPO_URL="https://github.com/<you>/websocket-demo-chat.git" ./ec2-setup.sh
#
# For a private repo, pass a URL with a personal access token embedded, e.g.:
#   REPO_URL="https://<token>@github.com/<you>/websocket-demo-chat.git" ./ec2-setup.sh
set -euo pipefail

REPO_URL="${REPO_URL:-https://github.com/ateekshaykh/websocket-demo-chat.git}"
APP_DIR="/opt/websocket-demo-chat"
PORT="${PORT:-8000}"
RUN_USER="${SUDO_USER:-$USER}"

sudo apt-get update -y
sudo apt-get install -y python3-venv python3-pip git

sudo mkdir -p "$APP_DIR"
sudo chown "$RUN_USER":"$RUN_USER" "$APP_DIR"

if [ -d "$APP_DIR/.git" ]; then
  git -C "$APP_DIR" pull
else
  git clone "$REPO_URL" "$APP_DIR"
fi

python3 -m venv "$APP_DIR/.venv"
"$APP_DIR/.venv/bin/pip" install --upgrade pip
"$APP_DIR/.venv/bin/pip" install -r "$APP_DIR/requirements.txt"

sudo tee /etc/systemd/system/websocket-chat.service > /dev/null <<EOF
[Unit]
Description=WebSocket Chat (FastAPI/uvicorn)
After=network.target

[Service]
Type=simple
User=$RUN_USER
WorkingDirectory=$APP_DIR
ExecStart=$APP_DIR/.venv/bin/uvicorn server:app --host 0.0.0.0 --port $PORT
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable websocket-chat
sudo systemctl restart websocket-chat

echo
echo "Deployed. Status:"
sudo systemctl status websocket-chat --no-pager -l || true
echo
echo "App should be reachable at: http://<EC2-public-ip>:$PORT/"
echo "Logs: sudo journalctl -u websocket-chat -f"
