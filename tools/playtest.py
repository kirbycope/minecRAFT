"""Plays minecRAFT through with a bot on a local server and checks each step: the raft, the current, Bruce, catching
flotsam, the island arriving, the Throwable Anchor, mooring, the island as blocks, casting off and the island
drifting away again.

The player is the bot from the Minecraft (Java) MCP server, driven through tools/mcp_bot.py, which must already be
serving and connected; the checks and the world's clock go through RCON. The MCP server has no tool to use an item
or click an entity, so two things are done another way. A click on the anchor's post is written into the record the
post's interaction entity keeps of who last clicked it, which is all a real click does. A cast cannot be faked (a
fishing hook cannot be summoned), so a second player, Fisher (tools/fisher.cjs, plain mineflayer), joins to cast and
reel in. Everything else is the MCP bot's own doing.

    python tools/playtest.py                                        # game on 25565, RCON on 25575
    python tools/playtest.py --rcon-port 25576 --game-port 25567    # the 26.1 server the bot plays on, see README.md
    python tools/playtest.py --headless                             # no players: CI, and any version the bot cannot join

--headless plays the same story without any player: the raft's chunks are force loaded, the anchor is set down,
thrown and broken by calling the pack's own functions where a player would act, and the steps only a player can do
(the bot's view of the world, casting) are left out.
"""

import argparse
import glob
import os
import json
import re
import subprocess
import sys
import time

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from rcon import Rcon  # noqa: E402

BOT = "ClaudeBot"
RAFT = (8, 105, 8)
results: list[tuple[str, bool, str]] = []


def bot(tool: str, **arguments) -> str:
    out = subprocess.run([sys.executable, __file__.rsplit("/", 1)[0] + "/mcp_bot.py", "call", tool, json.dumps(arguments)],
                         capture_output=True, text=True, timeout=300)
    return (out.stdout + out.stderr).strip()


def check(name: str, ok: bool, detail: str = "") -> bool:
    results.append((name, ok, detail))
    print(f"{'PASS' if ok else 'FAIL'}  {name}{'  (' + detail + ')' if detail else ''}", flush=True)
    return ok


def number(reply: str) -> float | None:
    match = re.search(r"(-?\d+(?:\.\d+)?)", reply.split(":", 1)[-1] if "has the following" in reply else reply)
    return float(match.group(1)) if match else None


def count(r: Rcon, selector: str) -> int:
    reply = r.command(f"execute if entity {selector}")
    match = re.search(r"Count: (\d+)", reply)
    return int(match.group(1)) if match else 0


def score(r: Rcon, holder: str, objective: str = "raft.state") -> int | None:
    match = re.search(r"has (-?\d+) \[", r.command(f"scoreboard players get {holder} {objective}"))
    return int(match.group(1)) if match else None


def wait_for(predicate, seconds: float, step: float = 0.5) -> bool:
    end = time.time() + seconds
    while time.time() < end:
        if predicate():
            return True
        time.sleep(step)
    return predicate()


def uuid_of(r: Rcon, target: str) -> str:
    match = re.search(r"\[I; ?(-?\d+), ?(-?\d+), ?(-?\d+), ?(-?\d+)\]", r.command(f"data get entity {target} UUID"))
    return "[I;" + ",".join(match.groups()) + "]" if match else ""


def start_fisher(port: int):
    """Fisher, a plain mineflayer client (tools/fisher.cjs), using the mineflayer the MCP server installed."""
    found = glob.glob(os.path.expanduser("~/.npm/_npx/*/node_modules/mineflayer"))
    if not found:
        return None
    env = dict(os.environ, MINEFLAYER=found[0], PORT=str(port), PATH="/opt/homebrew/bin:" + os.environ.get("PATH", ""))
    process = subprocess.Popen(["node", os.path.join(os.path.dirname(os.path.abspath(__file__)), "fisher.cjs")],
                               stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, env=env, bufsize=1)
    line = process.stdout.readline().strip()
    return process if line.startswith("ok") else None


def tell(process, line: str) -> str:
    process.stdin.write(line + "\n")
    process.stdin.flush()
    return process.stdout.readline().strip()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--rcon-port", type=int, default=25575)
    parser.add_argument("--password", default="minecraft")
    parser.add_argument("--game-port", type=int, default=25565, help="where Fisher joins (the bot's server)")
    parser.add_argument("--headless", action="store_true", help="no bot and no Fisher; see above")
    args = parser.parse_args()
    r = None
    for _ in range(240):   # a server just started takes a while to open RCON
        try:
            r = Rcon(port=args.rcon_port, password=args.password)
            break
        except OSError:
            time.sleep(0.5)
    if r is None:
        print(f"no RCON on port {args.rcon_port}")
        return 1

    headless = args.headless

    # A clean slate: no island, no anchor, the bot back on the raft at noon holding a fresh kit. Headless, the raft's
    # stretch of ocean is force loaded instead, as a player standing on it would keep it.
    for command in ["function raft:island/clear", "function raft:anchor/clear", "time set noon", "weather clear",
                    "kill @e[type=minecraft:item]"]:
        r.command(command)
    if headless:
        r.command("forceload add -112 -16 80 48")
        wait_for(lambda: score(r, "#raft_placed") == 1, 20)
    else:
        for command in [f"tp {BOT} 9 106 9", f"clear {BOT}", f"give {BOT} minecraft:fishing_rod",
                        f"execute as {BOT} run function raft:anchor/give"]:
            r.command(command)
    time.sleep(1)

    # The raft and the kit.
    check("the raft is four jungle planks at y 105", all("passed" in r.command(f"execute if block {x} 105 {z} minecraft:jungle_planks")
                                                          for x in (8, 9) for z in (8, 9)))
    if not headless:
        info = bot("get-block-info", x=8, y=105, z=8)
        check("the bot sees jungle planks under it", "jungle_planks" in info, info.splitlines()[0] if info else "")
        inventory = bot("list-inventory")
        check("the bot holds a fishing rod and a Throwable Anchor", "fishing_rod" in inventory and "oak_fence" in inventory,
              inventory.replace("\n", " ")[:120])
        unlocked = r.command(f"recipe give {BOT} raft:throwable_anchor")
        check("the anchor recipe was already unlocked", "Unlocked 0" in unlocked or "No new" in unlocked or "unlock" not in unlocked.lower(), unlocked)

    # The current.
    flotsam = count(r, "@e[tag=flotsam]")
    check("flotsam is floating in the stream", flotsam >= 5, f"{flotsam} pieces")
    # One piece with room to drift before it is gone (at x 48), followed for two seconds.
    r.command("tag @e[tag=flotsam,tag=!hooked,x=-40,y=95,z=-20,dx=80,dy=20,dz=40,limit=1] add playtest.track")
    x0 = number(r.command("data get entity @e[tag=playtest.track,limit=1] Pos[0]"))
    time.sleep(2)
    x1 = number(r.command("data get entity @e[tag=playtest.track,limit=1] Pos[0]"))
    r.command("tag @e[tag=playtest.track] remove playtest.track")
    check("flotsam drifts east with the current", x0 is not None and x1 is not None and 0.5 < x1 - x0 < 4,
          f"x {x0} -> {x1}")
    if not headless:
        check("Bruce the dolphin is near the raft", count(r, "@e[type=minecraft:dolphin,tag=raft.bruce,x=9,y=105,z=9,distance=..64]") == 1)

    # Catching: Fisher casts off the raft's side, a barrel drifts into the bobber and rides on the line, and
    # reeling in gives Fisher 4 to 6 items.
    fisher = None if headless else start_fisher(args.game_port)
    if not headless and check("a second player joins to fish", fisher is not None):
        r.command("tp Fisher 9.5 106 9.5 90 20")
        r.command("clear Fisher")
        r.command("give Fisher minecraft:fishing_rod")
        r.command("kill @e[tag=flotsam]")
        tell(fisher, "look 3 105.9 9.5")
        tell(fisher, "cast")
        landed = wait_for(lambda: "passed" in r.command("execute as @e[type=minecraft:fishing_bobber] at @s if block ~ ~ ~ minecraft:water"), 5)
        bob_x = number(r.command("data get entity @e[type=minecraft:fishing_bobber,limit=1] Pos[0]"))
        bob_z = number(r.command("data get entity @e[type=minecraft:fishing_bobber,limit=1] Pos[2]"))
        check("the cast lands in the water", landed and bob_x is not None, f"bobber at {bob_x}, {bob_z}")
        if bob_x is not None:
            # Three blocks upstream of the bobber: the current brings it in within about two seconds.
            r.command(f"function raft:flotsam/summon/barrel {{x:{bob_x - 3:.2f},z:{bob_z:.2f},yaw:30}}")
            r.command("tag @e[tag=raft.new] add bob.a")
            r.command("tag @e[tag=raft.new] remove raft.new")
            caught = wait_for(lambda: count(r, "@e[tag=flotsam.barrel,tag=hooked]") == 1, 6)
            check("a barrel drifting into the bobber is caught", caught)
            time.sleep(1)
            on_line = count(r, "@e[tag=flotsam.barrel,tag=hooked]") == 1
            check("it rides on the line while the line is out", on_line)
            r.command("execute as Fisher store result score #before raft.tmp run clear @s * 0")
            items_before = score(r, "#before", "raft.tmp") or 0
            tell(fisher, "reel")
            wait_for(lambda: count(r, "@e[tag=flotsam.barrel]") == 0, 3)
            time.sleep(0.3)
            r.command("execute as Fisher store result score #after raft.tmp run clear @s * 0")
            gained = (score(r, "#after", "raft.tmp") or 0) - items_before
            check("reeling in delivers the barrel's loot to whoever cast", 4 <= gained <= 6, f"{gained} items")
        tell(fisher, "quit")

    # The island: brought in from just upstream, slice by slice, and drifting toward the raft.
    r.command("function raft:island/start {x:-16}")
    wait_for(lambda: count(r, "@e[type=minecraft:block_display,tag=island.root]") == 9, 10)
    roots = count(r, "@e[type=minecraft:block_display,tag=island.root]")
    drawn = count(r, "@e[type=minecraft:block_display,tag=island,tag=!island.root]")
    check("the island arrives as 9 slices of display entities", roots == 9 and drawn == 767, f"{roots} roots, {drawn} entities")
    x_a = score(r, "#island_x")
    time.sleep(1)
    x_b = score(r, "#island_x")
    check("the island drifts with the current", x_a is not None and x_b is not None and x_b > x_a, f"{x_a} -> {x_b}")
    root_x = number(r.command("data get entity @e[type=minecraft:block_display,tag=island.s0,tag=island.root,limit=1] Pos[0]"))
    passenger_x = number(r.command("execute as @e[type=minecraft:block_display,tag=island.s0,tag=island.root,limit=1] on passengers run data get entity @s Pos[0]"))
    check("each slice's entities ride its root", root_x is not None and passenger_x is not None and abs(root_x - passenger_x) < 0.01,
          f"root {root_x}, passenger {passenger_x}")

    # The anchor: set down on the raft by the bot, then thrown.
    if headless:
        placed = r.command("execute positioned 9.5 106 8.5 run function raft:anchor/set_down {yaw:180}")
    else:
        owner = uuid_of(r, BOT)
        bot("equip-item", itemName="oak_fence")
        placed = bot("place-block", x=9, y=106, z=8, faceDirection="down")
    ok = wait_for(lambda: score(r, "#anchor") == 1, 3)
    check("placing the anchor on the raft sets it down", ok, placed.splitlines()[0] if placed else "")
    parts = ("passed" in r.command("execute if block 9 106 8 minecraft:oak_fence"), count(r, "@e[type=minecraft:interaction,tag=raft.post]"),
             count(r, "@e[type=minecraft:frog,tag=raft.carrier]"), count(r, "@e[type=minecraft:block_display,tag=raft.anchor]"))
    check("the post, its interaction box and the anchor are there", parts == (True, 1, 1, 6),
          f"post {parts[0]}, {parts[1]} interaction, {parts[2]} frog, {parts[3]} anchor parts")
    time.sleep(1)   # the lead is tied, and its knot hung, on the anchor's first tick
    check("the anchor is tied to the post by a lead", count(r, "@e[type=minecraft:leash_knot,x=9,y=106,z=8,distance=..1.5]") == 1
          and "[I;" in r.command("data get entity @e[type=minecraft:frog,tag=raft.carrier,limit=1] leash"))
    if headless:
        r.command("function raft:anchor/use")
    else:
        r.command(f"data modify entity @e[type=minecraft:interaction,tag=raft.post,limit=1] interaction set value {{player:{owner},timestamp:0L}}")
    thrown = wait_for(lambda: score(r, "#anchor") == 2, 2)
    check("using the post throws the anchor", thrown)
    wait_for(lambda: score(r, "#throw") == 0, 4)
    frog_y = number(r.command("data get entity @e[type=minecraft:frog,tag=raft.carrier,limit=1] Pos[1]"))
    frog_x = number(r.command("data get entity @e[type=minecraft:frog,tag=raft.carrier,limit=1] Pos[0]"))
    frog_z = number(r.command("data get entity @e[type=minecraft:frog,tag=raft.carrier,limit=1] Pos[2]"))
    check("the anchor lands in the water off the raft's edge and sinks", frog_y is not None and frog_y < 104 and frog_z is not None and frog_z < 7,
          f"anchor at {frog_x}, {frog_y}, {frog_z}")
    check("the lead still holds after the throw", "[I;" in r.command("data get entity @e[type=minecraft:frog,tag=raft.carrier,limit=1] leash"))

    # Mooring: the island settles on a whole block and becomes real blocks.
    moored = wait_for(lambda: score(r, "#island") == 2, 15)
    ix = (score(r, "#island_x") or 0) // 1000
    check("the anchored island moors on a whole block", moored and (score(r, "#island_x") or 1) % 1000 == 0, f"origin x {ix}")
    check("its entities are gone", count(r, "@e[type=minecraft:block_display,tag=island]") == 0)
    stone = sum("passed" in r.command(f"execute if block {ix + x} {105 + y} {10 + z} #minecraft:base_stone_overworld")
                for x, y, z in ((14, 5, 7), (3, 5, 6), (14, 0, 7), (20, -3, 6)))
    check("the island stands as rock", stone >= 3, f"{stone} of 4 rock samples")
    chest = r.command(f"data get block {ix + 3} {105 + 12} {10 + 6} LootTable")
    check("the hut's chest holds the Mountain Loot Box table", "raft:chests/mountain_loot_box" in chest, chest[:100])
    if not headless:
        seen = bot("get-block-info", x=ix + 14, y=105 + 12, z=10 + 7)
        check("the bot sees the island's top", "moss" in seen or "stone" in seen or "andesite" in seen, seen.splitlines()[0] if seen else "")

    # Break into it, then cast off: break the anchor's post.
    r.command(f"setblock {ix + 14} {105 + 4} {10 + 2} minecraft:air")
    # Headless, the post is simply removed, which is the path a post broken by anything but a click takes.
    dug = r.command("setblock 9 106 8 minecraft:air") if headless else bot("dig-block", x=9, y=106, z=8)
    gone = wait_for(lambda: score(r, "#anchor") == 0, 3)
    check("breaking the post destroys the anchor", gone, dug.splitlines()[0] if dug else "")
    check("post, anchor, knot and lead are all gone", "passed" not in r.command("execute if block 9 106 8 minecraft:oak_fence")
          and count(r, "@e[tag=raft.anchor]") == 0 and count(r, "@e[type=minecraft:leash_knot]") == 0)
    time.sleep(0.3)
    check("no lead is left lying about", count(r, "@e[type=minecraft:item,nbt={Item:{id:\"minecraft:lead\"}}]") == 0)
    cast = wait_for(lambda: score(r, "#island") == 1, 5)
    roots = count(r, "@e[type=minecraft:block_display,tag=island.root]")
    drawn = count(r, "@e[type=minecraft:block_display,tag=island,tag=!island.root]")
    # Whole, it is 767 entities; the hole broken into it is drawn block by block, a few more.
    check("casting off turns the island back into entities", cast and roots == 9 and 760 <= drawn <= 800, f"{roots} roots, {drawn} entities")
    water = sum("passed" in r.command(f"execute if block {ix + x} {105 + y} {10 + z} minecraft:water")
                for x, y, z in ((14, 0, 7), (20, -3, 6)))
    air = sum("passed" in r.command(f"execute if block {ix + x} {105 + y} {10 + z} minecraft:air") for x, y, z in ((14, 5, 7), (3, 5, 6)))
    check("its blocks are ocean again", water == 2 and air == 2, f"{water} water, {air} air")
    check("the hut's loot floated out", count(r, f"@e[type=minecraft:item,x={ix + 3},y={105 + 12},z={10 + 6},distance=..3]") >= 1)
    x_a = score(r, "#island_x")
    time.sleep(1)
    check("the island drifts on", (score(r, "#island_x") or 0) > (x_a or 0))
    if not headless:
        check("the bot is still in the game", "Current position" in bot("get-position"))

    r.command("function raft:island/clear")
    if headless:
        r.command("forceload remove all")
    failed = [name for name, ok, _ in results if not ok]
    print(f"\n{len(results) - len(failed)} of {len(results)} passed" + (f"; failed: {', '.join(failed)}" if failed else ""))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
