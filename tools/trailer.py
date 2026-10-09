"""Films the minecRAFT trailer on the local server with the Java client on this Mac, one shot at a time, as
minecRAFT-bedrock's tools/trailer.py does for Bedrock.

Commands go to the server over RCON (tools/rcon.py) and real input to the client through tools/client_drive.py.
The camera is the player spectating an invisible item display, the dolly, which this script teleports every tick
along an eased path; the display's teleport_duration makes the client glide it between ticks, so the moves come out
smooth. A mannequin wearing the player's skin stands in for them on the raft, since a spectator has no body. Each
take is the game's picture and sound, recorded together by tools/sck_capture.py into trailer/takes/<name>.mp4.

    python tools/trailer.py prep            # filming state: morning, clear, no island, the anchor set down on the raft
    python tools/trailer.py shot <name>     # films one shot (the SHOTS below, in trailer order)
    python tools/trailer.py reset           # gives the player their body and HUD back

The client runs fullscreen with music off and the HUD hidden (F1, which toggles; this script keeps track of it in
trailer/takes/.hud). tools/trailer_cut.py cuts the takes into the trailer.
"""

import json
import math
import os
import re
import subprocess
import sys
import threading
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from rcon import Rcon  # noqa: E402
import client_drive as cd  # noqa: E402

TAKES = os.path.join(ROOT, "trailer", "takes")
PYTHON = sys.executable
P = "Kirbycope"
ANCHOR = ('minecraft:oak_fence[minecraft:item_name="Throwable Anchor",minecraft:item_model="minecraft:heavy_core",'
          'minecraft:max_stack_size=5,minecraft:custom_data={raft_anchor:true}]')

r = Rcon()


def run(*commands):
    for c in commands:
        out = r.command(c)
        if any(word in out for word in ("Unknown", "Incorrect", "Expected", "Invalid")):
            print(f"  ! {c} -> {out.strip()}")


def score(holder, objective="raft.state"):
    m = re.search(r"has (-?\d+) \[", r.command(f"scoreboard players get {holder} {objective}"))
    return int(m.group(1)) if m else None


# --- the HUD ------------------------------------------------------------------------------------------------------

HUD_STATE = os.path.join(TAKES, ".hud")


def hud(hidden: bool):
    """F1 toggles the HUD, so whether it is hidden now is remembered between runs."""
    os.makedirs(TAKES, exist_ok=True)
    now = open(HUD_STATE).read().strip() == "hidden" if os.path.exists(HUD_STATE) else False
    cd.focus()
    if now != hidden:
        cd.key("f1")
        time.sleep(0.2)
    open(HUD_STATE, "w").write("hidden" if hidden else "shown")


# --- the camera ---------------------------------------------------------------------------------------------------

def ease(t, kind):
    if kind == "linear": return t
    return 0.5 - 0.5 * math.cos(math.pi * t)


def dolly():
    """The player watches through the dolly: an item display holding nothing, which the client glides."""
    if "passed" not in r.command("execute if entity @e[type=minecraft:item_display,tag=camera]"):
        run('summon minecraft:item_display 9 120 9 {Tags:["camera"],teleport_duration:2}')
    run(f"gamemode spectator {P}", f"spectate @e[type=minecraft:item_display,tag=camera,limit=1] {P}")


def cam(pos, look):
    run(f"tp @e[type=minecraft:item_display,tag=camera,limit=1] {pos[0]:.3f} {pos[1]:.3f} {pos[2]:.3f} facing {look[0]:.3f} {look[1]:.3f} {look[2]:.3f}")


def move(a, look_a, b, look_b, seconds, kind="sine"):
    """From a (looking at look_a) to b (looking at look_b), a teleport a tick, eased."""
    start, n = time.perf_counter(), 0
    while True:
        t = min(1.0, (time.perf_counter() - start) / seconds)
        e = ease(t, kind)
        cam([p + (q - p) * e for p, q in zip(a, b)], [p + (q - p) * e for p, q in zip(look_a, look_b)])
        if t >= 1.0: break
        n += 1
        time.sleep(max(0.0, start + n * 0.05 - time.perf_counter()))


def first_person(pos, yaw, pitch):
    """The player's own view, for the shots where they do something."""
    run(f"execute as {P} run spectate", f"gamemode survival {P}", f"tp {P} {pos[0]} {pos[1]} {pos[2]} {yaw} {pitch}")


# --- recording ----------------------------------------------------------------------------------------------------

def record(name, seconds):
    os.makedirs(TAKES, exist_ok=True)
    return subprocess.Popen([PYTHON, os.path.join(ROOT, "tools", "sck_capture.py"), os.path.join(TAKES, f"{name}.mp4"), str(seconds)])


def standin(on: bool, yaw=90):
    """Killing and summoning it again would leave a puff of smoke in the next take, so one already there is turned."""
    if on and "passed" in r.command("execute if entity @e[type=minecraft:mannequin,tag=standin]"):
        run(f"tp @e[type=minecraft:mannequin,tag=standin] 9.5 106 9.5 {yaw} 10")
        return
    run("kill @e[type=minecraft:mannequin,tag=standin]")
    if on:
        run(f'summon minecraft:mannequin 9.5 106 9.5 {{Tags:["standin"],profile:{{name:"{P}"}},Invulnerable:1b,immovable:1b,'
            f'Rotation:[{yaw}f,10f],equipment:{{mainhand:{{id:"minecraft:fishing_rod",count:1}}}}}}')


def piece(x, z, kind, bob="bob.a"):
    """One piece of flotsam put in the current where the camera will see it."""
    run(f'function raft:flotsam/summon/{kind} {{x:{x},z:{z},yaw:{(x * 37) % 360},bob:"{bob}"}}')


def island_x():
    return (score("#island_x") or 0) // 1000


# --- setting up ---------------------------------------------------------------------------------------------------

def prep():
    run("gamerule minecraft:send_command_feedback false", "gamerule minecraft:command_block_output false",
        "gamerule minecraft:advance_time false", "gamerule minecraft:advance_weather false", "time set 2000", "weather clear",
        "function raft:island/clear", "function raft:anchor/clear", "kill @e[type=minecraft:item]",
        "kill @e[type=minecraft:item_display,tag=camera]", "scoreboard players set #island1_seen raft.state 1",
        f"clear {P}", f"give {P} minecraft:fishing_rod", f"item replace entity {P} hotbar.8 with {ANCHOR}",
        # every recipe and advancement already had, so no toast slides in over a take
        f"recipe give {P} *", f"advancement grant {P} everything", f"xp set {P} 0 levels", f"xp set {P} 0 points")
    # Set the anchor down for real: stand on the raft, look at the top of the plank by its north edge, use the anchor.
    standin(False)
    # (tp ... facing aims from the feet, not the eyes, so the angle is given: from the eyes, 1.6 blocks above the
    # plank's top and a block short of its middle, that is 58 degrees down.)
    first_person((9.5, 106, 9.5), 180, 58)
    hud(True)
    time.sleep(1.0)
    cd.focus(); cd.hotbar(9); time.sleep(0.3); cd.use(); time.sleep(1.0)
    print("anchor set down:", score("#anchor") == 1, "post:", r.command("execute if block 9 106 8 minecraft:oak_fence").strip())
    cd.hotbar(1)


# --- the shots, in trailer order ----------------------------------------------------------------------------------

def shot_open():
    hud(True); standin(True, 90); dolly()
    a, b, look = (28, 115, -18), (13, 107.6, 3.5), (9, 106.6, 9.2)
    cam(a, look); time.sleep(1.5)
    rec = record("open", 11); time.sleep(0.8)
    move(a, look, b, look, 9)
    rec.wait()


def shot_drift():
    hud(True); standin(True, 90); dolly()
    # Low over the water, easing upstream while the pieces come down past the camera's right.
    run("kill @e[tag=flotsam]")
    for x, z, kind, bob in ((-4, 2.2, "barrel", "bob.a"), (-7, 3.6, "plank", "bob.b"), (-10, 1.8, "palm_leaf", "bob.a"),
                            (-13, 3.2, "plastic", "bob.b"), (-16, 2.0, "plank", "bob.a"), (-19, 3.8, "barrel", "bob.b"),
                            (-22, 2.4, "palm_leaf", "bob.a")):
        piece(x, z, kind, bob)
    a, la, b, lb = (2, 106.45, 0.6), (-14, 105.9, 4.2), (-3, 106.6, 0.4), (-17, 105.9, 4.6)
    cam(a, la); time.sleep(1.5)
    rec = record("drift", 10); time.sleep(0.5)
    move(a, la, b, lb, 8.5, "linear")
    rec.wait()


def shot_fish():
    """First person, with the hand and hotbar: cast, a barrel drifts into the bobber, reel it in."""
    standin(False); hud(False)
    first_person((8.5, 106, 9.5), 100, 14)
    run("kill @e[tag=flotsam]")
    time.sleep(1.5)
    cd.focus(); cd.hotbar(1)
    rec = record("fish", 14); time.sleep(1.5)
    cd.use(); time.sleep(2.2)
    m = re.findall(r"(-?\d+\.\d+)d", r.command("data get entity @e[type=minecraft:fishing_bobber,limit=1] Pos"))
    if m:
        x, _, z = map(float, m)
        piece(round(x - 3, 2), round(z, 2), "barrel")
        end = time.time() + 8
        while time.time() < end and "passed" not in r.command("execute if entity @e[tag=hooked]"): time.sleep(0.3)
        time.sleep(2.0)
        cd.use()
    else:
        print("  ! no bobber in the water")
    rec.wait()


def shot_horizon():
    """Real time; the cut speeds it up. The island rises over the horizon slice by slice and comes on."""
    hud(True); standin(True, 90); dolly()
    run("function raft:island/clear", "function raft:island/start {x:-92}")
    a, la, b, lb = (11, 108.5, 5), (-32, 110, 18), (10, 108, 4.5), (-22, 109, 17)
    cam(a, la); time.sleep(0.5)
    rec = record("horizon", 70); time.sleep(10)
    move(a, la, b, lb, 55, "linear")
    rec.wait()


def shot_alongside():
    hud(True); standin(True, 180); dolly()
    while (score("#island_x") or -99999) < -24000: time.sleep(0.5)   # wait for it to come up beside the raft
    a, la, b, lb = (2, 112, -14), (-8, 112, 16), (12, 111, -12), (-2, 111, 16)
    cam(a, la); time.sleep(1)
    rec = record("alongside", 11); time.sleep(0.3)
    move(a, la, b, lb, 9.5, "linear")
    rec.wait()


def shot_anchor():
    """The anchor thrown off the raft; the island stops alongside."""
    hud(True); standin(True, 180); dolly()
    a, la, b, lb = (12.5, 107.8, 5.5), (7.5, 105.8, 9.5), (13.5, 108.5, 4), (5, 103, 9.5)
    cam(a, la); time.sleep(1)
    rec = record("anchor", 10); time.sleep(1.5)
    run(f"execute as {P} run function raft:anchor/use")
    time.sleep(1.5)
    move(a, la, b, lb, 5)
    rec.wait()
    end = time.time() + 30
    while time.time() < end and score("#island") != 2: time.sleep(0.5)
    print("moored at", island_x())


def shot_explore():
    ox = island_x()
    hud(True); standin(True, 180); dolly()
    a, la = (ox + 40, 112, 2), (ox + 16, 112, 16)
    b, lb = (ox + 30, 122, -2), (ox + 12, 114, 16)
    c, lc = (ox + 4, 126, 0), (ox + 5, 116, 16)
    cam(a, la); time.sleep(1)
    rec = record("explore", 17); time.sleep(0.3)
    move(a, la, b, lb, 7.5)
    move(b, lb, c, lc, 7.5)
    rec.wait()


def shot_hut():
    ox = island_x()
    hud(True); dolly()
    a, b, look = (ox + 9, 121, 10), (ox + 1, 121.5, 9.5), (ox + 3.5, 118, 16)
    cam(a, look); time.sleep(1)
    rec = record("hut", 9); time.sleep(0.3)
    move(a, look, b, look, 7.5)
    rec.wait()


def shot_underwater():
    ox = island_x()
    hud(True); dolly()
    # Beside the sunken anchor, the lead running up to the raft overhead and the shelf's seagrass beyond.
    a, la, b, lb = (14, 102.8, 1.5), (9.5, 101.8, 6), (6.5, 102.6, 2.2), (8.5, 101.8, 7)
    cam(a, la); time.sleep(1)
    rec = record("underwater", 10); time.sleep(0.3)
    move(a, la, b, lb, 8.5, "linear")
    rec.wait()


def shot_castoff():
    """The post is broken; the island lets go and drifts away. Real time; the cut speeds up the drift."""
    hud(True); standin(True, 180); dolly()
    a, la = (13, 108, 4.5), (7, 106, 9.5)
    b, lb = (20, 118, -16), (18, 108, 16)
    c, lc = (34, 116, -14), (38, 108, 16)
    cam(a, la); time.sleep(1)
    rec = record("castoff", 45); time.sleep(1.5)
    run("function raft:anchor/destroy", "playsound minecraft:block.wood.break block @a 9 106 8")
    time.sleep(2)
    move(a, la, b, lb, 6)
    time.sleep(1)
    move(b, lb, c, lc, 28, "linear")
    rec.wait()


def shot_end():
    hud(True); standin(True, 270); dolly()
    run("function raft:island/clear")
    a, b, look = (14, 108, 3), (26, 118, -14), (9, 106.6, 9.2)
    cam(a, look); time.sleep(1)
    rec = record("end", 9); time.sleep(0.3)
    move(a, look, b, look, 7.5)
    rec.wait()


def moor():
    """The island brought in alongside and the anchor set down and thrown, so the moored shots can be filmed again."""
    prep()
    run("function raft:island/start {x:-16}")
    time.sleep(1)
    run(f"execute as {P} run function raft:anchor/use")
    end = time.time() + 40
    while time.time() < end and score("#island") != 2: time.sleep(0.5)
    print("moored at", island_x())


def reset():
    standin(False)
    run(f"execute as {P} run spectate", "kill @e[type=minecraft:item_display,tag=camera]", f"gamemode survival {P}", f"tp {P} 9.5 106 9.5",
        "gamerule minecraft:send_command_feedback true", "gamerule minecraft:command_block_output true",
        "gamerule minecraft:advance_time true", "gamerule minecraft:advance_weather true")
    hud(False)


SHOTS = {name[5:]: fn for name, fn in list(globals().items()) if name.startswith("shot_")}

if __name__ == "__main__":
    what, *args = sys.argv[1:]
    if what == "prep": prep()
    elif what == "shot":
        SHOTS[args[0]]()
        print(os.path.join(TAKES, f"{args[0]}.mp4"))
    elif what == "reset": reset()
    elif what == "moor": moor()
    elif what == "cam": dolly(); cam(tuple(map(float, args[:3])), tuple(map(float, args[3:6])))
