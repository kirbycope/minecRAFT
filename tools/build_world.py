"""Builds minecRAFT.zip, the world as players install it, from the repository, so nothing is zipped by hand.

The archive holds one folder, minecRAFT/, which is unzipped into Minecraft's saves folder: level.dat, icon.png,
data/minecraft/ (the flat ocean's generator settings and the game rules) and datapacks/raft/. There are no region
files, so the game generates the ocean when the world is first opened. Only files git tracks go in.

    python tools/build_world.py            # writes build/minecRAFT.zip
    python tools/build_world.py --check    # exits 1 if the archive on disk differs from a fresh build
"""

import argparse
import io
import os
import subprocess
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORLD = "world"
OUTPUT = os.path.join(ROOT, "build", "minecRAFT.zip")
FOLDER = "minecRAFT"
STAMP = (2026, 1, 1, 0, 0, 0)   # a fixed timestamp keeps the archive byte-for-byte reproducible, so --check can compare it
STORED = {".png", ".jpg", ".jpeg", ".dat"}   # already compressed (level.dat and the .dat files are gzipped NBT)


def tracked() -> list[str]:
    out = subprocess.run(["git", "-C", ROOT, "ls-files", "-z", "--", WORLD], check=True, capture_output=True).stdout.decode("utf-8")
    return sorted(p[len(WORLD) + 1:] for p in out.split("\0") if p and os.path.isfile(os.path.join(ROOT, p)))


def build() -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        seen: set[str] = set()
        for relative in tracked():
            path = f"{FOLDER}/{relative}"
            parts = path.split("/")
            for depth in range(1, len(parts)):
                folder = "/".join(parts[:depth]) + "/"
                if folder not in seen:
                    seen.add(folder)
                    info = zipfile.ZipInfo(folder, STAMP)
                    info.external_attr = 0o40755 << 16
                    archive.writestr(info, b"", zipfile.ZIP_STORED)
            info = zipfile.ZipInfo(path, STAMP)
            info.external_attr = 0o644 << 16
            info.compress_type = zipfile.ZIP_STORED if os.path.splitext(path)[1].lower() in STORED else zipfile.ZIP_DEFLATED
            with open(os.path.join(ROOT, WORLD, relative), "rb") as handle:
                archive.writestr(info, handle.read(), compresslevel=9)
    return buffer.getvalue()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="report whether the archive is up to date instead of writing it")
    parser.add_argument("--output", default=OUTPUT)
    args = parser.parse_args()
    data = build()
    current = os.path.exists(args.output) and open(args.output, "rb").read() == data
    if args.check:
        print("up to date" if current else f"out of date: {os.path.relpath(args.output, ROOT)}")
        return 0 if current else 1
    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    with open(args.output, "wb") as handle:
        handle.write(data)
    print(f"wrote {os.path.relpath(args.output, ROOT)} ({len(data)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
