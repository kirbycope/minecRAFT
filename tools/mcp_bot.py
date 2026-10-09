"""Drives a player bot through the Minecraft (Java) MCP server, yuniko-software/minecraft-mcp-server, for playtests.

That server is a stdio MCP server wrapping a mineflayer bot. This script is its MCP client: `serve` starts it (the
same command as the `minecraft` entry in the workspace's .mcp.json), keeps the bot in the game, and takes tool calls
over a small HTTP endpoint on localhost, so each `call` can be a separate command while the bot stays connected.

    python tools/mcp_bot.py serve                              # start the bot (localhost:25565, user ClaudeBot)
    python tools/mcp_bot.py tools                              # list the MCP server's tools
    python tools/mcp_bot.py call get-position                  # call one, arguments as JSON
    python tools/mcp_bot.py call send-chat '{"message": "/function raft:island/start {x:-16}"}'

mineflayer speaks Java Edition up to 26.1, so against a newer server the bot connects through ViaProxy
(https://github.com/ViaVersion/ViaProxy), which translates the protocol; see README.md.
"""

import argparse
import http.server
import json
import os
import subprocess
import sys
import threading
import urllib.request

PORT = 8790
COMMAND = ["npx", "-y", "github:yuniko-software/minecraft-mcp-server"]


class Session:
    """One MCP stdio session: JSON-RPC requests out, one response per line back."""

    def __init__(self, command: list[str]):
        env = dict(os.environ)
        env["PATH"] = "/opt/homebrew/bin:" + env.get("PATH", "")
        self.process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=sys.stderr,
                                        env=env, text=True, bufsize=1)
        self.next_id = 0
        self.lock = threading.Lock()
        self.request("initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                                    "clientInfo": {"name": "minecRAFT-playtest", "version": "1.0"}})
        self.notify("notifications/initialized")

    def notify(self, method: str, params: dict | None = None) -> None:
        self.process.stdin.write(json.dumps({"jsonrpc": "2.0", "method": method, "params": params or {}}) + "\n")
        self.process.stdin.flush()

    def request(self, method: str, params: dict) -> dict:
        with self.lock:
            self.next_id += 1
            request_id = self.next_id
            self.process.stdin.write(json.dumps({"jsonrpc": "2.0", "id": request_id, "method": method, "params": params}) + "\n")
            self.process.stdin.flush()
            while True:
                line = self.process.stdout.readline()
                if not line:
                    raise ConnectionError("the MCP server exited")
                try:
                    message = json.loads(line)
                except json.JSONDecodeError:
                    continue   # anything the server prints that is not protocol
                if message.get("id") == request_id:
                    if "error" in message:
                        return {"error": message["error"]}
                    return message.get("result", {})


def serve(args: argparse.Namespace) -> None:
    session = Session(COMMAND + ["--host", args.host, "--port", str(args.port), "--username", args.username])

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_POST(self):
            body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            if body.get("method") == "tools/list":
                result = session.request("tools/list", {})
            else:
                result = session.request("tools/call", {"name": body["tool"], "arguments": body.get("arguments", {})})
            data = json.dumps(result).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def log_message(self, *_):
            pass

    print(f"MCP bot {args.username} -> {args.host}:{args.port}; tool calls on http://127.0.0.1:{PORT}", flush=True)
    http.server.ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()


def post(body: dict) -> dict:
    request = urllib.request.Request(f"http://127.0.0.1:{PORT}", data=json.dumps(body).encode("utf-8"),
                                     headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=300) as response:
        return json.loads(response.read())


def text_of(result: dict) -> str:
    if "error" in result:
        return f"ERROR {result['error']}"
    return "\n".join(part.get("text", json.dumps(part)) for part in result.get("content", []))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="verb", required=True)
    s = sub.add_parser("serve")
    s.add_argument("--host", default="localhost")
    s.add_argument("--port", type=int, default=25565)
    s.add_argument("--username", default="ClaudeBot")
    sub.add_parser("tools")
    c = sub.add_parser("call")
    c.add_argument("tool")
    c.add_argument("arguments", nargs="?", default="{}")
    args = parser.parse_args()
    if args.verb == "serve":
        serve(args)
    elif args.verb == "tools":
        for tool in post({"method": "tools/list"}).get("tools", []):
            print(f"{tool['name']}: {tool.get('description', '')}\n    {json.dumps(tool.get('inputSchema', {}).get('properties', {}))}")
    else:
        print(text_of(post({"tool": args.tool, "arguments": json.loads(args.arguments)})))
    return 0


if __name__ == "__main__":
    sys.exit(main())
