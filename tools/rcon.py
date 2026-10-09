"""A minimal RCON client for a local Java Edition server, used by the smoke test and to drive a dev server.

    python tools/rcon.py "time set noon" "weather clear"      # each argument is one command; prints each reply
    python tools/rcon.py --port 25575 --password minecraft "list"

The server needs enable-rcon=true, rcon.port and rcon.password in server.properties.
"""

import argparse
import socket
import struct
import sys


class Rcon:
    def __init__(self, host: str = "127.0.0.1", port: int = 25575, password: str = "minecraft", timeout: float = 30.0):
        self.sock = socket.create_connection((host, port), timeout=timeout)
        self.next_id = 1
        if self._request(3, password)[0] == -1:
            raise PermissionError("RCON password rejected")

    def _send(self, kind: int, body: str) -> int:
        request_id = self.next_id
        self.next_id += 1
        payload = struct.pack("<ii", request_id, kind) + body.encode("utf-8") + b"\x00\x00"
        self.sock.sendall(struct.pack("<i", len(payload)) + payload)
        return request_id

    def _read(self) -> tuple[int, str]:
        def exactly(n: int) -> bytes:
            data = b""
            while len(data) < n:
                chunk = self.sock.recv(n - len(data))
                if not chunk:
                    raise ConnectionError("RCON connection closed")
                data += chunk
            return data
        (length,) = struct.unpack("<i", exactly(4))
        packet = exactly(length)
        request_id, _ = struct.unpack("<ii", packet[:8])
        return request_id, packet[8:-2].decode("utf-8", "replace")

    def _request(self, kind: int, body: str) -> tuple[int, str]:
        self._send(kind, body)
        return self._read()

    def command(self, command: str) -> str:
        # The server splits a reply longer than 4096 bytes over several packets and marks none of them as the
        # last, so after the first one the rest are read until a short silence.
        request_id = self._send(2, command)
        parts = []
        reply_id, body = self._read()
        if reply_id == request_id:
            parts.append(body)
        if len(body.encode("utf-8")) >= 4096:
            timeout = self.sock.gettimeout()
            self.sock.settimeout(0.2)
            try:
                while True:
                    reply_id, body = self._read()
                    if reply_id == request_id:
                        parts.append(body)
            except (TimeoutError, socket.timeout):
                pass
            finally:
                self.sock.settimeout(timeout)
        return "".join(parts)

    def close(self) -> None:
        self.sock.close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=25575)
    parser.add_argument("--password", default="minecraft")
    parser.add_argument("commands", nargs="+")
    args = parser.parse_args()
    rcon = Rcon(args.host, args.port, args.password)
    for command in args.commands:
        print(rcon.command(command))
    rcon.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
