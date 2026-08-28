"""
Python WebSocket chat client.

Connects to the same FastAPI server and room as the HTML/JS client, so
messages sent from either side show up on both.

Usage:
    python python_client.py --host localhost:8000 --room general --username alice
    python python_client.py --host my-app.onrender.com --secure --room general --username bob
"""
import argparse
import asyncio
import json
import sys

import websockets


async def receive_loop(ws) -> None:
    async for raw in ws:
        data = json.loads(raw)
        if data.get("type") in ("system", "roster"):
            print(f"\r* {data['message']} ({data.get('users_online', '?')} online)")
        elif data.get("type") == "typing":
            print(f"\r* {data.get('username')} is typing...")
        else:
            print(f"\r[{data.get('username')}] {data.get('message')}")
        print("> ", end="", flush=True)


async def send_loop(ws) -> None:
    loop = asyncio.get_event_loop()
    while True:
        text = await loop.run_in_executor(None, lambda: sys.stdin.readline())
        text = text.strip()
        if not text:
            print("> ", end="", flush=True)
            continue
        if text in ("/quit", "/exit"):
            await ws.close()
            return
        await ws.send(json.dumps({"message": text}))


async def main() -> None:
    parser = argparse.ArgumentParser(description="Python WebSocket chat client")
    parser.add_argument("--host", default="localhost:8000", help="host[:port] of the server, e.g. my-app.onrender.com")
    parser.add_argument("--room", default="general", help="room name to join")
    parser.add_argument("--username", required=True, help="your display name")
    parser.add_argument("--secure", action="store_true", help="use wss:// instead of ws:// (use for Render deployments)")
    args = parser.parse_args()

    scheme = "wss" if args.secure else "ws"
    url = f"{scheme}://{args.host}/ws/{args.room}/{args.username}"

    print(f"Connecting to {url} ...")
    async with websockets.connect(url) as ws:
        print(f"Connected. Type messages and press Enter (/quit to exit).")
        print("> ", end="", flush=True)
        receiver = asyncio.create_task(receive_loop(ws))
        sender = asyncio.create_task(send_loop(ws))
        done, pending = await asyncio.wait(
            {receiver, sender}, return_when=asyncio.FIRST_COMPLETED
        )
        for task in pending:
            task.cancel()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBye.")
