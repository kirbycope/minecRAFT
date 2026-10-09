"""Writes the data pack's before_26_3 overlay: every function that summons a block display, in the form 26.1 and 26.2 read.

Java Edition 26.3 changed a block display's block_state from {Name:"...",Properties:{...}} to
{id:"...",properties:{...}}, and each version reads only its own form (the other comes out as air). The pack is
written for 26.3; this copies each function that uses the new form into world/datapacks/raft/before_26_3/ with the
old one, and pack.mcmeta applies that folder over the pack on formats before 26.3's. tools/island.py runs this after
it writes the island, so the overlay never falls behind; run it by hand after editing a function that summons one.

    python tools/overlay.py
"""

import os
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PACK = os.path.join(ROOT, "world", "datapacks", "raft")
OVERLAY = os.path.join(PACK, "before_26_3")


def main() -> None:
    if os.path.isdir(OVERLAY):
        shutil.rmtree(OVERLAY)
    written = 0
    base = os.path.join(PACK, "data")
    for folder, _, files in os.walk(base):
        for name in files:
            if not name.endswith(".mcfunction"):
                continue
            with open(os.path.join(folder, name), encoding="utf-8") as handle:
                text = handle.read()
            if "block_state:{id:" not in text:
                continue
            old = text.replace("block_state:{id:", "block_state:{Name:").replace(",properties:{", ",Properties:{")
            target = os.path.join(OVERLAY, "data", os.path.relpath(folder, base), name)
            os.makedirs(os.path.dirname(target), exist_ok=True)
            with open(target, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(old)
            written += 1
    print(f"wrote {written} functions into {os.path.relpath(OVERLAY, ROOT)}")


if __name__ == "__main__":
    main()
