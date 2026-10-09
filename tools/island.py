"""Builds Raft's Small Island 1 as voxels and writes it into the data pack as functions.

Small Island 1, from https://raft.fandom.com/wiki/Small_Tropical_Islands: a rock pillar with an abandoned hut and a
Mountain Loot Box on top, a tiered rock mass with grassy ledges, a long sloping tail that runs down to a sandy tip,
2 mango trees, 4 palm trees, a pineapple plant, 2 watermelon plants, 5 flowers of each of the five colours, and
under the water a sandy shelf with metal ore, copper, sand, clay, stone, seaweed and 2 giant clams.

The voxels are the same island minecRAFT-bedrock builds (its tools/island.py, same seed), so both editions meet
the same island. Local coordinates: x runs with the current (the island's long axis), z across it, and y = 0 is the
top layer of the ocean (world y 105), so y >= 1 is above water. Every function below runs positioned at the
island's origin, local (0, 0, 0), so it can be anywhere along its drift:

- island/slice/<n>: summons one slice of the island, four blocks of it along x, as an empty block_display (the
  slice's root) carrying the display entities that draw it as passengers. Moving the island is then one teleport
  per slice. Only voxels with an exposed face and no deeper than DISPLAY_DEPTH are drawn, runs of rock merged into
  2x2x2 cubes drawn at scale 2.
- island/place: every block the island is made of, inside included, filled in only where the ocean is (water or
  air), so nothing built is overwritten. Solids bottom up, then plants, so each has its ground when it is placed.
- island/lift: redraws whatever of the island is still standing as display entities, cube for cube where a cube
  is still whole, and block by block from what is left where a player has broken into it.
- island/sink: returns every block still as it was placed to ocean, plants first and top down so none pops off
  as an item, and empties the hut's chest onto the water.

    python tools/island.py              # writes world/datapacks/raft/data/raft/function/island/generated/ (and the
                                        # before_26_3 overlay, through tools/overlay.py)
    python tools/island.py --preview    # also writes build/island1_top.png and build/island1_side.png
"""

import argparse
import math
import os
import random
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FUNCTIONS = os.path.join(ROOT, "world", "datapacks", "raft", "data", "raft", "function")
OUT = os.path.join(FUNCTIONS, "island", "generated")
DISPLAY_DEPTH = -2   # voxels deeper than this are only seen once the island is real blocks
SLICE = 4            # blocks of x per slice

# block state for commands, whether it is drawn while drifting, whether a 2x2x2 run of it may be one entity
PALETTE = {
    "stone": ("minecraft:stone", True, True),
    "andesite": ("minecraft:andesite", True, True),
    "moss": ("minecraft:moss_block", True, False),
    "sand": ("minecraft:sand", True, False),
    "clay": ("minecraft:clay", True, False),
    "iron_ore": ("minecraft:iron_ore", True, False),
    "copper_ore": ("minecraft:copper_ore", True, False),
    "palm_log": ("minecraft:jungle_log[axis=y]", True, False),
    "mango_log": ("minecraft:oak_log[axis=y]", True, False),
    "palm_leaves": ("minecraft:azalea_leaves[persistent=true]", True, False),
    "mango_leaves": ("minecraft:flowering_azalea_leaves[persistent=true]", True, False),
    "melon": ("minecraft:melon", True, False),
    "planks": ("minecraft:oak_planks", True, False),
    "red_wool": ("minecraft:red_wool", True, False),
    "blue_wool": ("minecraft:blue_wool", True, False),
    "chest": ("minecraft:chest[facing=south]", True, False),
    "red_flower": ("minecraft:poppy", True, False),
    "blue_flower": ("minecraft:cornflower", True, False),
    "yellow_flower": ("minecraft:dandelion", True, False),
    "white_flower": ("minecraft:lily_of_the_valley", True, False),
    "black_flower": ("minecraft:wither_rose", True, False),
    "pineapple": ("minecraft:sweet_berry_bush[age=3]", True, False),
    "ladder": ("minecraft:ladder[facing=east]", True, False),
    "seagrass": ("minecraft:seagrass", False, False),
    "kelp": ("minecraft:kelp[age=25]", False, False),          # the top of a column, fully grown so it stays put
    "kelp_plant": ("minecraft:kelp_plant", False, False),      # the rest of the column
    "clam": ("minecraft:sea_pickle[pickles=3,waterlogged=true]", False, False),
}
SOLID = {"stone", "andesite", "moss", "sand", "clay", "iron_ore", "copper_ore", "palm_log", "mango_log", "melon",
         "planks", "red_wool", "blue_wool", "chest", "palm_leaves", "mango_leaves"}
ROCK = {"stone", "andesite"}


def ellipse(x, z, cx, cz, rx, rz):
    return ((x - cx) / rx) ** 2 + ((z - cz) / rz) ** 2


def build() -> dict:
    """The island's voxels, exactly as minecRAFT-bedrock's tools/island.py builds them."""
    rng = random.Random(1)
    v: dict[tuple[int, int, int], str] = {}

    # Above water, a top height for each column.
    top: dict[tuple[int, int], int] = {}
    for x in range(-2, 36):
        for z in range(-2, 18):
            h = None
            if ellipse(x, z, 3, 6, 2.7, 3.0) <= 1: h = 11                               # the pillar
            elif 5 <= x <= 8 and 4 <= z <= 8: h = 6                                     # the saddle between
            elif ellipse(x, z, 14, 7, 6.0, 5.2) <= 1:                                   # the main rock
                h = 12 if z >= 7 else 9 if z >= 4 else 5
                if x >= 18: h = min(h, 8)
            elif 18 <= x <= 32 and 4 <= z <= 9 - max(0, x - 26) // 2:                  # the tail, sloping to the water
                h = max(1, round(7 - (x - 18) * 6 / 13))
            elif 31 <= x <= 33 and 5 <= z <= 7: h = 1                                   # the hump at the tip
            elif 11 <= x <= 18 and 12 <= z <= 13: h = 1                                 # the beach on the far side
            if h is not None:
                top[(x, z)] = h

    # A walkable way up: from the tail onto the right of the main rock, then the ledges, then the top.
    for (x, z), h in {(19, 5): 7, (19, 6): 7, (18, 6): 8, (17, 6): 9, (16, 6): 9, (15, 6): 10, (15, 7): 11, (15, 8): 12,
                      (9, 5): 7, (8, 5): 6}.items():
        top[(x, z)] = h
    # Overhanging cap on the pillar, like the reference's flat-topped stack.
    cap = [(x, z) for x in range(0, 7) for z in range(2, 11) if ellipse(x, z, 3, 6, 3.4, 3.6) <= 1 and (x, z) not in top]

    for (x, z), h in top.items():
        for y in range(-1, h + 1):
            rock = "andesite" if rng.random() < 0.25 else "stone"
            v[(x, y, z)] = rock
        # surface: moss on ledges above the beach line, sand on the low tail and the beach
        if h <= 2: v[(x, h, z)] = "sand"
        elif h <= 3 and x >= 22: v[(x, h, z)] = "sand"
        else: v[(x, h, z)] = "moss" if h in (5, 8, 9, 12) or (x, z) in {(15, 7), (15, 6)} else v[(x, h, z)]
    for (x, z) in cap:
        for y in (10, 11):
            v[(x, y, z)] = "stone"
        v[(x, 11, z)] = "moss"

    # Under water, the shelf: the island's footprint grows with depth, more toward the tail, then tapers to a point.
    foot = set(top) | set(cap)
    for y in range(-2, -13, -1):
        depth = -y
        grow = min((depth - 1) * 0.9, 4.5) if depth <= 7 else max(4.5 - (depth - 7) * 1.0, 0)
        for x in range(-10, 44):
            for z in range(-10, 26):
                if (x, y, z) in v: continue
                d = min((math.hypot(x - fx, (z - fz) * 1.1) for fx, fz in foot if abs(x - fx) <= 8 and abs(z - fz) <= 8), default=99)
                reach = grow + (2.0 if x > 18 and depth >= 3 else 0) + (1.0 if z > 9 and depth >= 3 else 0) + rng.uniform(-0.6, 0.6)
                if d <= reach:
                    v[(x, y, z)] = "stone"
    # The shelf top is the first layer with nothing above it: sand there, clay in patches; boulders on it.
    for (x, y, z), b in list(v.items()):
        if y <= -2 and b in ROCK and (x, y + 1, z) not in v:
            v[(x, y, z)] = "clay" if rng.random() < 0.18 else "sand"
    for _ in range(9):
        bx, bz = rng.randint(-4, 38), rng.randint(-4, 20)
        floor = max((y for (x, y, z) in v if x == bx and z == bz), default=None)
        if floor is None or floor >= 0: continue
        for dx in (0, 1):
            for dz in (0, 1):
                for dy in (1, 2):
                    if (bx + dx, floor + dy, bz + dz) not in v and floor + dy <= -1:
                        v[(bx + dx, floor + dy, bz + dz)] = "andesite"

    def exposed(x, y, z):
        return any(v.get(n) not in SOLID for n in ((x + 1, y, z), (x - 1, y, z), (x, y + 1, z), (x, y - 1, z), (x, y, z + 1), (x, y, z - 1)))

    # Ores on the rock walls just under the water: 7 metal ore and 5 copper, in pairs and threes like the game.
    walls = sorted(p for p, b in v.items() if b in ROCK and -6 <= p[1] <= -1 and exposed(*p))
    rng.shuffle(walls)
    for kind, n in (("iron_ore", 7), ("copper_ore", 5)):
        placed = 0
        for p in walls:
            if placed >= n: break
            if v[p] in ROCK:
                v[p] = kind; placed += 1
                q = (p[0], p[1] - 1, p[2])
                if placed < n and v.get(q) in ROCK and exposed(*q):
                    v[q] = kind; placed += 1

    plants: dict[tuple[int, int, int], str] = {}

    def ground(x, z):
        ys = [y for (xx, y, zz), b in v.items() if xx == x and zz == z and b in SOLID]
        return max(ys) if ys else None

    def palm(x, z, lean=(0, 0), height=6):
        g = ground(x, z)
        px, pz = x, z
        for i in range(1, height + 1):
            if i == height // 2 + 1: px, pz = px + lean[0], pz + lean[1]
            v[(px, g + i, pz)] = "palm_log"
        cy = g + height + 1
        v[(px, cy, pz)] = "palm_leaves"
        for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            for r in (1, 2):
                v[(px + dx * r, cy, pz + dz * r)] = "palm_leaves"
            v[(px + dx * 3, cy - 1, pz + dz * 3)] = "palm_leaves"
        for dx, dz in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
            v[(px + dx, cy, pz + dz)] = "palm_leaves"
            v[(px + dx * 2, cy - 1, pz + dz * 2)] = "palm_leaves"

    def mango(x, z):
        g = ground(x, z)
        for i in range(1, 4):
            v[(x, g + i, z)] = "mango_log"
        for dx in range(-2, 3):
            for dz in range(-2, 3):
                for dy in (3, 4, 5):
                    if abs(dx) + abs(dz) + abs(dy - 4) * 2 <= 3 and (x + dx, g + dy, z + dz) not in v:
                        v[(x + dx, g + dy, z + dz)] = "mango_leaves"

    # 4 palm trees: one on top, one on the front ledge, one leaning off the right of the main rock, one on the tail.
    palm(13, 9, height=6)
    palm(12, 3, height=5)
    palm(18, 7, lean=(1, 0), height=5)
    palm(23, 6, lean=(1, 0), height=5)
    # 2 mango trees on the middle ledge and the top.
    mango(10, 5)
    mango(16, 10)

    # The hut on the pillar: a 3x3 floor of planks, posts, a red and blue tarp roof, the loot box inside.
    g = 11
    for dx in range(-1, 2):
        for dz in range(-1, 2):
            v[(3 + dx, g, 6 + dz)] = "planks"
    for dx, dz in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        for dy in (1, 2):
            v[(3 + dx, g + dy, 6 + dz)] = "planks"
    for dx in range(-1, 2):
        for dz in range(-1, 2):
            v[(3 + dx, g + 3, 6 + dz)] = "red_wool" if dz < 1 else "blue_wool"
    v[(3, g + 1, 6)] = "chest"
    # A ladder up the pillar's saddle side, from the saddle to the hut.
    for y in range(7, 11):
        plants[(6, y, 6)] = "ladder"

    # Plants on free ground: pineapple, 2 watermelons, 5 of each flower.
    def free_ground(region):
        spots = []
        for (x, z) in region:
            gy = ground(x, z)
            if gy is None or gy < 1 or v.get((x, gy, z)) not in ("moss", "sand"): continue
            if (x, gy + 1, z) in v or (x, gy + 1, z) in plants: continue
            spots.append((x, gy + 1, z))
        rng.shuffle(spots)
        return spots

    grassy = [p for p in free_ground(list(top)) if v.get((p[0], p[1] - 1, p[2])) == "moss"]
    for kind, n in (("pineapple", 1), ("melon", 2), ("red_flower", 5), ("blue_flower", 5), ("yellow_flower", 5), ("white_flower", 5), ("black_flower", 5)):
        for _ in range(n):
            if not grassy: break
            p = grassy.pop()
            if kind == "melon": v[p] = "melon"
            else: plants[p] = kind

    # Under water: seagrass on the sand, kelp along the shelf's edge, 2 giant clams.
    seabed = [(x, y + 1, z) for (x, y, z), b in v.items() if b in ("sand", "clay") and y <= -3 and (x, y + 1, z) not in v]
    rng.shuffle(seabed)
    for p in seabed[:120]:
        plants[p] = "seagrass"
    for p in seabed[120:134]:
        for dy in range(0, rng.randint(3, 6)):
            q = (p[0], p[1] + dy, p[2])
            if q[1] > -1 or q in v: break   # a kelp column stops at the surface or at rock
            plants[q] = "kelp"
    for p in seabed[134:136]:
        plants[p] = "clam"

    # Java Edition draws a kelp column as kelp_plant under a single kelp head.
    for (x, y, z), b in list(plants.items()):
        if b == "kelp" and plants.get((x, y + 1, z)) == "kelp":
            plants[(x, y, z)] = "kelp_plant"

    return {"voxels": v, "plants": plants}


def display_units(v: dict, plants: dict) -> list:
    """The entities that draw the island: exposed voxels down to DISPLAY_DEPTH, rock merged into 2x2x2 cubes.
    As (x, y, z, name, size), the cube's low corner."""
    def solid(p):
        return v.get(p) in SOLID

    def exposed(p):
        x, y, z = p
        return any(not solid(n) for n in ((x + 1, y, z), (x - 1, y, z), (x, y + 1, z), (x, y - 1, z), (x, y, z + 1), (x, y, z - 1)))

    shown = {p for p in v if p[1] >= DISPLAY_DEPTH and exposed(p)}
    claimed: set = set()
    out = []
    for p in sorted(shown):
        if p in claimed: continue
        b = v[p]
        if PALETTE[b][2]:
            merged = False
            for ox, oy, oz in ((0, 0, 0), (-1, 0, 0), (0, 0, -1), (-1, 0, -1), (0, -1, 0), (-1, -1, 0), (0, -1, -1), (-1, -1, -1)):
                corner = (p[0] + ox, p[1] + oy, p[2] + oz)
                cube = [(corner[0] + dx, corner[1] + dy, corner[2] + dz) for dx in (0, 1) for dy in (0, 1) for dz in (0, 1)]
                if all(v.get(c) in ROCK and c not in claimed for c in cube):
                    claimed.update(cube)
                    out.append((corner[0], corner[1], corner[2], b, 2))
                    merged = True
                    break
            if merged: continue
        claimed.add(p)
        out.append((p[0], p[1], p[2], b, 1))
    for p, b in sorted(plants.items()):
        if PALETTE[b][1] and p[1] >= DISPLAY_DEPTH:
            out.append((p[0], p[1], p[2], b, 1))
    return out


def block_snbt(state: str) -> str:
    """minecraft:jungle_log[axis=y] -> {id:"minecraft:jungle_log",properties:{axis:"y"}}"""
    if "[" not in state:
        return f'{{id:"{state}"}}'
    name, props = state[:-1].split("[")
    pairs = ",".join(f'{k}:"{val}"' for k, val in (p.split("=") for p in props.split(",")))
    return f'{{id:"{name}",properties:{{{pairs}}}}}'


def block_name(state: str) -> str:
    return state.split("[")[0]


def num(value: float) -> str:
    return f"{value:g}"


def display_snbt(dx: int, y: int, z: int, b: str, size: int, tags: list[str]) -> str:
    """One display entity drawing a voxel (or a 2x2x2 cube) at an offset from its slice's root."""
    tag_list = ",".join(f'"{t}"' for t in tags)
    s = num(size)
    return (f'{{id:"minecraft:block_display",Tags:[{tag_list}],view_range:2f,block_state:{block_snbt(PALETTE[b][0])},'
            f'transformation:{{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],'
            f'translation:[{num(dx)}f,{num(y)}f,{num(z)}f],scale:[{s}f,{s}f,{s}f]}}}}')


def root_snbt(n: int) -> str:
    # The root draws nothing itself; it is what moves, and the client glides it over two ticks per teleport.
    return (f'{{Tags:["island","island.root","island.s{n}"],teleport_duration:2,view_range:2f,'
            f'block_state:{{id:"minecraft:air"}}')


def runs(cells: list[tuple[int, int, int, str]]) -> list[tuple[int, int, int, int, str]]:
    """Merges cells in order into runs along x of the same block: (x0, x1, y, z, name)."""
    out: list[list] = []
    for x, y, z, b in cells:
        if out and out[-1][2] == y and out[-1][3] == z and out[-1][4] == b and out[-1][1] == x - 1:
            out[-1][1] = x
        else:
            out.append([x, x, y, z, b])
    return [tuple(r) for r in out]


def rel(x: int, y: int, z: int) -> str:
    return f"~{x or ''} ~{y or ''} ~{z or ''}"


def write(name: str, lines: list[str], about: str) -> None:
    path = os.path.join(OUT, name + ".mcfunction")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(f"# Generated by tools/island.py: {about} Do not edit by hand.\n")
        handle.write("\n".join(lines) + "\n")


def generate(v: dict, plants: dict) -> dict:
    units = display_units(v, plants)
    every = {**v, **plants}
    xs = [p[0] for p in every]; zs = [p[2] for p in every]
    min_x = min(p[0] for p in units)
    slices = (max(p[0] + p[4] for p in units) - min_x + SLICE - 1) // SLICE

    def slice_of(x: int) -> int:
        return (x - min_x) // SLICE

    if os.path.isdir(OUT):
        shutil.rmtree(OUT)

    # The slices: the root at the slice's low x, the island's z = 0 and the ocean's top layer.
    by_slice: dict[int, list] = {}
    for unit in units:
        by_slice.setdefault(slice_of(unit[0]), []).append(unit)
    for n in range(slices):
        ox = min_x + n * SLICE
        passengers = ",".join(display_snbt(x - ox, y, z, b, size, ["island"]) for x, y, z, b, size in by_slice.get(n, []))
        write(f"slice/{n}", [f"execute unless loaded {rel(ox, 0, 0)} run return fail",
                             f"summon minecraft:block_display {rel(ox, 0, 0)} {root_snbt(n)},Passengers:[{passengers}]}}",
                             "return 1"],
              f"slice {n} of Small Island 1, x {ox}..{ox + SLICE - 1}, as display entities riding its root.")

    # Placing: solids bottom up, then plants bottom up, filled only into ocean. The chest is placed on its own,
    # with the Mountain Loot Box table the first time and empty after.
    solids = sorted(((x, y, z, b) for (x, y, z), b in v.items()), key=lambda c: (c[1], c[2], c[0]))
    growing = sorted(((x, y, z, b) for (x, y, z), b in plants.items()), key=lambda c: (c[1], c[2], c[0]))
    place = []
    for x0, x1, y, z, b in runs([c for c in solids if c[3] != "chest"]) + runs(growing):
        place.append(f"fill {rel(x0, y, z)} {rel(x1, y, z)} {PALETTE[b][0]} replace #raft:ocean")
    chest = next((x, y, z) for (x, y, z), b in v.items() if b == "chest")
    place.append(f"execute if score #chest_filled raft.state matches 0 run setblock {rel(*chest)} {PALETTE['chest'][0]}"
                 '{LootTable:"raft:chests/mountain_loot_box"} keep')
    place.append(f"setblock {rel(*chest)} {PALETTE['chest'][0]} keep")
    place.append("scoreboard players set #chest_filled raft.state 1")
    write("place", place, "every block of Small Island 1, filled into the ocean where it is moored.")

    # Lifting. First, which of the drawn units are still whole: a score per unit, 1 if every cell of it is still
    # the block it was placed as.
    unit_of: dict[tuple[int, int, int], int] = {}
    lift = ["scoreboard players reset * raft.cover"]
    for i, (x, y, z, b, size) in enumerate(units):
        cells = [(x + dx, y + dy, z + dz) for dx in range(size) for dy in range(size) for dz in range(size)]
        for c in cells:
            unit_of[c] = i
        # each cell as it was built: a rock cube can be stone and andesite mixed, drawn as one of them
        checks = " ".join(f"if block {rel(*c)} {block_name(PALETTE[every[c]][0])}" for c in cells)
        lift.append(f"execute store success score #u{i} raft.cover {checks}")
    # The slices' roots, then each whole unit drawn as it arrived.
    for n in range(slices):
        lift.append(f"summon minecraft:block_display {rel(min_x + n * SLICE, 0, 0)} {root_snbt(n)}}}")
    for i, (x, y, z, b, size) in enumerate(units):
        n = slice_of(x)
        ox = min_x + n * SLICE
        lift.append(f"execute if score #u{i} raft.cover matches 1 run summon minecraft:block_display {rel(ox, 0, 0)} "
                    + display_snbt(x - ox, y, z, b, size, ["island", "island.new", f"island.s{n}"])[len('{id:"minecraft:block_display",'):].join(["{", ""]))
    # Then what is left of anything broken into: every remaining block not under a whole unit that has a face
    # open to something no longer there (or never solid).
    for (x, y, z), b in sorted(every.items(), key=lambda kv: (kv[0][1], kv[0][0], kv[0][2])):
        if y < DISPLAY_DEPTH or not PALETTE[b][1] or (x, y, z) in plants:
            continue   # a plant is a unit of its own, drawn above if it is still there
        n = slice_of(x) if min_x <= x < min_x + slices * SLICE else None
        if n is None:
            continue
        ox = min_x + n * SLICE
        unit = unit_of.get((x, y, z))
        guard = f"if score #u{unit} raft.cover matches 0 " if unit is not None else ""
        neighbours = [(x + 1, y, z), (x - 1, y, z), (x, y + 1, z), (x, y - 1, z), (x, y, z + 1), (x, y, z - 1)]
        summon = (f"summon minecraft:block_display {rel(ox, 0, 0)} "
                  + display_snbt(x - ox, y, z, b, 1, ["island", "island.new", f"island.s{n}"])[len('{id:"minecraft:block_display",'):].join(["{", ""]))
        here = f"if block {rel(x, y, z)} {block_name(PALETTE[b][0])}"
        if any(v.get(q) not in SOLID for q in neighbours):
            # Open to the water or air (or to a plant) as built; only a whole unit hides it.
            if unit is None:
                continue   # every exposed block at this depth belongs to a unit; nothing to do
            lift.append(f"execute {guard}{here} run {summon}")
        else:
            # Buried as built: drawn only if a neighbour has since been broken.
            checks = " ".join(f"if block {rel(*q)} {block_name(PALETTE[v[q]][0])}" for q in neighbours)
            lift.append(f"execute {guard}{here} store success score #shut raft.tmp {checks}")
            lift.append(f"execute {guard}{here} if score #shut raft.tmp matches 0 run {summon}")
    for n in range(slices):
        lift.append(f"execute as @e[type=minecraft:block_display,tag=island.new,tag=island.s{n}] run ride @s mount "
                    f"@e[type=minecraft:block_display,tag=island.root,tag=island.s{n},limit=1]")
    lift.append("tag @e[type=minecraft:block_display,tag=island.new] remove island.new")
    write("lift", lift, "what is left of Small Island 1 drawn again as display entities, before it sinks.")

    # Sinking: plants top down, then solids top down, each back to water at or under the surface and air above.
    sink = []
    chest_line = f"execute if block {rel(*chest)} minecraft:chest positioned {rel(*chest)} run function raft:island/empty_chest"
    order = runs(sorted(((x, y, z, b) for (x, y, z), b in plants.items()), key=lambda c: (-c[1], c[2], c[0])))
    order += runs(sorted(((x, y, z, b) for (x, y, z), b in v.items() if b != "chest"), key=lambda c: (-c[1], c[2], c[0])))
    sink.append(chest_line)
    for x0, x1, y, z, b in order:
        sink.append(f"fill {rel(x0, y, z)} {rel(x1, y, z)} {'minecraft:water' if y <= 0 else 'minecraft:air'} replace {block_name(PALETTE[b][0])}")
    write("sink", sink, "every block of Small Island 1 still standing returned to the ocean.")

    bounds = {"min_x": min(xs), "max_x": max(xs), "min_z": min(zs), "max_z": max(zs), "slice_x": min_x, "slices": slices}
    # Whether the island's chunks are loaded, so the conversion never runs half done.
    write("loaded", [f"execute if loaded {rel(bounds['min_x'], 0, bounds['min_z'])} if loaded {rel(bounds['max_x'], 0, bounds['min_z'])} "
                     f"if loaded {rel(bounds['min_x'], 0, bounds['max_z'])} if loaded {rel(bounds['max_x'], 0, bounds['max_z'])} run return 1",
                     "return fail"], "whether all four corners of Small Island 1 are in loaded chunks.")
    write("constants", [f"scoreboard players set #slices raft.state {slices}"], "how many slices Small Island 1 is drawn in.")
    # Spawning a slice as it comes into range: the slices run downstream end first.
    spawn = []
    for n in reversed(range(slices)):
        spawn.append(f"execute if score #slice_next raft.state matches {slices - 1 - n} "
                     f"if score #edge raft.tmp matches {-(min_x + (n + 1) * SLICE) * 1000}.. "
                     f"run return run function raft:island/spawn_slice {{n:{n}}}")
    spawn.append("return fail")
    write("spawn_next", spawn, "spawns the next slice of Small Island 1 once its downstream edge is in range.")
    return {"blocks": len(v) + len(plants), "units": len(units), "cubes": sum(1 for u in units if u[4] == 2),
            "slices": slices, "bounds": bounds, "lift_lines": len(lift), "place_lines": len(place), "sink_lines": len(sink)}


def preview(v: dict, plants: dict, out_dir: str) -> None:
    from PIL import Image
    colours = {"stone": (150, 150, 150), "andesite": (130, 130, 130), "moss": (90, 140, 50), "sand": (220, 205, 150), "clay": (160, 165, 180),
               "iron_ore": (200, 160, 130), "copper_ore": (200, 110, 70), "palm_log": (110, 85, 50), "mango_log": (120, 95, 60),
               "palm_leaves": (70, 170, 60), "mango_leaves": (110, 160, 90), "melon": (120, 170, 40), "planks": (170, 130, 80),
               "red_wool": (180, 40, 40), "blue_wool": (50, 70, 180), "chest": (150, 100, 40)}
    xs = [p[0] for p in v]; ys = [p[1] for p in v]; zs = [p[2] for p in v]
    s = 12
    w, h = (max(xs) - min(xs) + 1), (max(zs) - min(zs) + 1)
    img = Image.new("RGB", (w * s, h * s), (20, 40, 90))
    best = {}
    for (x, y, z), b in v.items():
        if (x, z) not in best or y > best[(x, z)][0]: best[(x, z)] = (y, b)
    for (x, z), (y, b) in best.items():
        c = colours.get(b, (255, 0, 255))
        if y < 0: c = tuple(int(ch * 0.45 + d) for ch, d in zip(c, (10, 25, 60)))
        img.paste(c, ((x - min(xs)) * s, (z - min(zs)) * s, (x - min(xs) + 1) * s, (z - min(zs) + 1) * s))
    img.save(os.path.join(out_dir, "island1_top.png"))
    w, h = (max(xs) - min(xs) + 1), (max(ys) - min(ys) + 1)
    img = Image.new("RGB", (w * s, h * s), (120, 190, 230))
    near = {}
    for (x, y, z), b in v.items():
        if (x, y) not in near or z < near[(x, y)][0]: near[(x, y)] = (z, b)
    for (x, y), (z, b) in near.items():
        c = colours.get(b, (255, 0, 255))
        if y < 0: c = tuple(int(ch * 0.45 + d) for ch, d in zip(c, (10, 25, 60)))
        img.paste(c, ((x - min(xs)) * s, (max(ys) - y) * s, (x - min(xs) + 1) * s, (max(ys) - y + 1) * s))
    img.save(os.path.join(out_dir, "island1_side.png"))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--preview", action="store_true")
    args = parser.parse_args()

    island = build()
    stats = generate(island["voxels"], island["plants"])
    print(f"wrote {os.path.relpath(OUT, ROOT)}: {stats['blocks']} blocks, {stats['units']} display entities "
          f"({stats['cubes']} of them 2x2x2 rock) in {stats['slices']} slices; place {stats['place_lines']} commands, "
          f"lift {stats['lift_lines']}, sink {stats['sink_lines']}; bounds {stats['bounds']}")
    import overlay
    overlay.main()
    if args.preview:
        os.makedirs(os.path.join(ROOT, "build"), exist_ok=True)
        preview(island["voxels"], island["plants"], os.path.join(ROOT, "build"))
        print("previews in build/")


if __name__ == "__main__":
    main()
