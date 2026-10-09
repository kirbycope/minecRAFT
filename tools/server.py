"""Sets up a local Java Edition server running minecRAFT, for developing, for the bot to play on, and for CI.

Downloads the server for a version from Mojang, accepts the EULA, writes server.properties (offline mode so the bot
can join, RCON on, no whitelist, and the world kept ticking with nobody online so a headless playtest can run) and
puts the world in place as minecRAFT/. With --link the world's datapacks/raft is a link to this repository's, so an
edit is live after /reload; Minecraft only follows a link it is told to allow, which allowed_symlinks.txt does.

    python tools/server.py ../minecraft-java-server/26.3 --version 26.3 --port 25566 --link
    python tools/server.py build/server --version 26.1 --port 25567 --rcon-port 25576 --link
    cd <dir> && java -jar server.jar nogui

A world from a newer version cannot be opened by an older one, and 26.2 and later upgrade the world's files on first
load, which they refuse to do across a link: so with --link the first start on 26.2 or later is done with a copy,
and the link put in afterwards (`--link` again on the same folder).
"""

import argparse
import json
import os
import shutil
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORLD = os.path.join(ROOT, "world")
MANIFEST = "https://piston-meta.mojang.com/mc/game/version_manifest_v2.json"


def download(version: str, target: str) -> None:
    manifest = json.load(urllib.request.urlopen(MANIFEST))
    entry = next((v for v in manifest["versions"] if v["id"] == version), None)
    if entry is None:
        sys.exit(f"no such version: {version}")
    server = json.load(urllib.request.urlopen(entry["url"]))["downloads"]["server"]["url"]
    urllib.request.urlretrieve(server, target)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("dir")
    parser.add_argument("--version", default="26.3")
    parser.add_argument("--port", type=int, default=25565)
    parser.add_argument("--rcon-port", type=int, default=25575)
    parser.add_argument("--rcon-password", default="minecraft")
    parser.add_argument("--link", action="store_true", help="link the data pack instead of copying it")
    args = parser.parse_args()

    os.makedirs(args.dir, exist_ok=True)
    jar = os.path.join(args.dir, "server.jar")
    if not os.path.exists(jar):
        download(args.version, jar)
        print(f"downloaded the {args.version} server")
    with open(os.path.join(args.dir, "eula.txt"), "w") as handle:
        handle.write("eula=true\n")
    properties = {
        "level-name": "minecRAFT", "server-port": args.port, "online-mode": "false", "white-list": "false",
        "enable-rcon": "true", "rcon.port": args.rcon_port, "rcon.password": args.rcon_password,
        "spawn-protection": 0, "pause-when-empty-seconds": 0, "view-distance": 10, "simulation-distance": 10,
        "motd": f"minecRAFT ({args.version})",
    }
    with open(os.path.join(args.dir, "server.properties"), "w") as handle:
        handle.writelines(f"{key}={value}\n" for key, value in properties.items())
    with open(os.path.join(args.dir, "allowed_symlinks.txt"), "w") as handle:
        handle.write(f"[prefix]{os.path.join(WORLD, 'datapacks')}{os.sep}\n")

    level = os.path.join(args.dir, "minecRAFT")
    if not os.path.exists(os.path.join(level, "level.dat")):
        os.makedirs(level, exist_ok=True)
        for name in ("level.dat", "icon.png", "data"):
            source = os.path.join(WORLD, name)
            (shutil.copytree if os.path.isdir(source) else shutil.copy2)(source, os.path.join(level, name))
        fresh = True
    else:
        fresh = False
    pack = os.path.join(level, "datapacks", "raft")
    os.makedirs(os.path.dirname(pack), exist_ok=True)
    if os.path.islink(pack):
        os.unlink(pack)
    elif os.path.isdir(pack):
        shutil.rmtree(pack)
    if args.link and not (fresh and args.version != "26.1"):
        os.symlink(os.path.join(WORLD, "datapacks", "raft"), pack)
        print(f"{pack} -> the repository's data pack")
    else:
        shutil.copytree(os.path.join(WORLD, "datapacks", "raft"), pack)
        if args.link:
            print("copied the data pack for the first start; run this again with --link after it to link it")
    print(f"ready: cd {args.dir} && java -jar server.jar nogui")
    return 0


if __name__ == "__main__":
    sys.exit(main())
