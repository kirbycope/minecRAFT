![minecRAFT](/minecRAFT.png)

# minecRAFT
Raft but in Minecraft, for Java Edition 26.1 to 26.3. A data pack and a world, built from the game's own block and item
displays and nothing else: no mods, no resource pack. Its Bedrock Edition counterpart is
[minecRAFT-bedrock](https://github.com/kirbycope/minecRAFT-bedrock), and the two meet the same island.

You start on a 2x2 raft of jungle planks in an ocean that never ends, holding a fishing rod and a Throwable Anchor.
Debris drifts past on the current: barrels, planks, palm leaves and plastic. Cast your line so the bobber lands in its
path, and whatever floats into it is caught and rides on the line. Reel in to collect it. Bruce the dolphin swims
nearby.

| Flotsam | Looks like | Reeling it in gives |
| --- | --- | --- |
| Barrel | a small barrel | 4 to 6 rolls on Raft's barrel table: planks, sugar cane (plastic), jungle leaves (palm leaves), iron nuggets (scrap), string (rope), cobblestone (stone), beetroot, potato |
| Plank | a jungle board | 1 jungle planks |
| Palm leaf | a clump of leaves | 1 jungle leaves |
| Plastic | sugar cane, lying flat | 1 sugar cane |

Normal fishing still works alongside it.

### The first island
A couple of minutes into a new world, Raft's
[Small Island 1](https://raft.fandom.com/wiki/Small_Tropical_Islands) comes over the horizon and drifts toward the
raft: a rock pillar with an abandoned hut on top, a tiered rock mass with grassy ledges, a sloping sandy tail, four
palm trees, two mango trees, a pineapple bush, two watermelons, five flowers of each colour, and under the water a
sandy shelf with iron and copper ore, clay, seagrass, kelp and two sea pickles (the giant clams). It passes
alongside the raft and, left alone, drifts away again.

Throw your anchor while it is alongside and the raft stops, so the island does too: it becomes solid ground to climb,
chop, mine and explore. The hut's chest holds a roll on Raft's Mountain Loot Box table. When you are done, break the
anchor's post: the raft drifts on and the island floats away behind you, with whatever you dug out of it missing.

### The Throwable Anchor
Raft's [Throwable Anchor](https://raft.fandom.com/wiki/Throwable_Anchor): one item, used once.

1. Place it on the raft, like a block. A fence post goes up with the anchor beside it, tied to it by a lead.
2. Use the post (or the anchor) to throw it. It splashes down off the edge and sinks, and the raft is anchored.
3. Hit the post to pick it up. That destroys it, as in Raft, and the raft drifts again.

Placed on top of a plank, it is thrown off the nearest edge of the raft; placed against a plank's side, the post moves
up onto that plank and the anchor goes off that side. You start with one. More are crafted at a crafting table from
2 jungle planks, 3 string and 4 cobblestone (Raft's recipe is 2 planks, 4 rope and 4 stone, one more than a crafting
grid holds).

## Installation
1. Download `minecRAFT.zip` from the [latest release](https://github.com/kirbycope/minecRAFT/releases/latest)
1. Unzip it into the [saves folder](https://help.minecraft.net/hc/en-us/articles/4409159214605-Managing-Data-and-Game-Storage-in-Minecraft-Java-Edition)
   of Minecraft Java Edition, so the folder `minecRAFT` sits beside your other worlds
1. Open it from Singleplayer with Java Edition 26.1, 26.2 or 26.3. The world is saved in 26.1's format, so 26.2 and
   26.3 upgrade it when it first opens.

## How it works
- **The ocean** is the original map's superflat settings: bedrock, deepslate, stone, dirt and gravel, under 90
  layers of water in a Deep Ocean biome, with the surface at y 105. The world ships without region files, so the
  game generates the ocean itself, endlessly, as you look around.
- **The raft never moves.** Moving placed blocks can only be done a block at a time, so the current is shown by
  moving the debris past the raft instead.
- **The debris** is block and item displays teleported a short way downstream every tick (`flotsam/tick`). Each has a
  `teleport_duration`, so the client glides it between teleports rather than stepping it.
- **Catching** is `hook/tick`: every tick it finds each fishing hook, takes any debris within 1.6 blocks of it onto
  the line, and moves it with the hook. When the hook is gone because you reeled in, the loot table for that debris
  is rolled into the inventory of whoever cast it. A fishing hook does not keep its owner where a command can see
  it, so the caster is the nearest player holding a rod on the hook's first tick.
- **The island** is built by `tools/island.py` as voxels, the same voxels minecRAFT-bedrock builds, and written into
  the pack as functions: every block it is made of (7,973, inside included), and the 767 displays that draw it while
  it drifts (only blocks with an exposed face, no deeper than two below the surface, with runs of rock merged into
  2x2x2 cubes drawn at scale 2). The displays are split into 9 slices along the island's length; each slice is an
  empty block display carrying the rest as passengers, each offset by its transformation, so moving the island is
  nine teleports a tick. A slice is summoned as it comes within 56 blocks, so the island rises over the horizon.
  When the raft is anchored the island settles onto the next whole block and `island/generated/place` fills in the
  real blocks, only where the ocean is, so nothing built is overwritten. Casting off reverses it: every display unit
  whose blocks are still as they were placed is drawn again, anything broken into is drawn block by block from what
  is left, the blocks go back to ocean (plants first, so none pops off as an item), and the hut's chest spills
  whatever is left in it.
- **The anchor** is an oak fence item with a name, a heavy core's look and a mark in its `custom_data`. Placing one is
  noticed through the `minecraft.used:minecraft.oak_fence` statistic and what the player held a tick earlier, and a
  ray from their eyes finds the post. An interaction box over the post records who used it and who hit it. The anchor
  itself is six netherite block displays riding an invisible frog, because only a mob can be tied to a lead.

The tuning lives at the top of `raft:load`, with where each number is used.

### Versions
Java Edition 26.3 changed how a block display names its block, from `{Name:"...",Properties:{...}}` to
`{id:"...",properties:{...}}`, and each version reads only its own form. The pack is written for 26.3, and its
`before_26_3` overlay, which `pack.mcmeta` applies on 26.1 and 26.2, holds the functions that summon block displays
in the older form. `tools/overlay.py` writes it (`tools/island.py` runs it), so the two never drift apart.

## Repository layout
| Path | What it is |
| --- | --- |
| `world/` | The world as it ships: `level.dat`, `icon.png`, `data/minecraft/` (the ocean's generator settings and the game rules) and the data pack |
| `world/datapacks/raft/` | The data pack: `raft:load` and `raft:tick`, `flotsam/`, `hook/`, `bruce/`, `island/`, `anchor/`, the loot tables, the anchor's recipe |
| `world/datapacks/raft/data/raft/function/island/generated/` | Small Island 1, generated by `tools/island.py` |
| `world/datapacks/raft/before_26_3/` | The overlay for 26.1 and 26.2, generated by `tools/overlay.py` |
| `tools/island.py` | Builds Small Island 1 into the pack; `--preview` also draws top and side views into `build/` |
| `tools/anchor_arc.py` | Writes the anchor's throw, a teleport a tick |
| `tools/build_world.py` | Builds `minecRAFT.zip` |
| `tools/server.py` | Sets up a local server running the world |
| `tools/playtest.py` | Plays it through on a server and checks every step |
| `tools/mcp_bot.py`, `tools/fisher.cjs` | The players `playtest.py` uses |
| `tools/rcon.py` | A small RCON client |
| `tools/trailer.py`, `tools/trailer_cut.py`, `tools/client_drive.py`, `tools/sck_capture.py` | Film and cut the trailer |
| `trailer/edit.json`, `trailer/titles.json` | The trailer's edit list and title copy |

## Developing on a local server
`tools/server.py` sets up a server with the world in place and, with `--link`, the data pack linked to this
repository's, so an edit is live after `/reload`:

```bash
python tools/server.py ../minecraft-java-server/26.3 --version 26.3 --port 25566 --link
cd ../minecraft-java-server/26.3 && java -jar server.jar nogui
```

26.2 and later upgrade the world's files the first time they open it, and refuse to while the data pack is a link,
so on those the first start runs with a copy; run `server.py` with `--link` again afterwards to put the link in.

### Testing commands
| Command | Does |
| --- | --- |
| `/function raft:island/start {x:-92}` | Brings the island now, from over the horizon |
| `/function raft:island/start {x:-16}` | Brings it from just upstream of alongside, a few seconds away |
| `/function raft:island/clear` | Removes the island, entities or blocks |
| `/function raft:island/clear_at {x:-8}` | Also removes island blocks left standing with the island's origin at that x |
| `/function raft:anchor/clear` | Removes the anchor, post and lead without breaking them |
| `/function raft:anchor/give` | Another anchor |

In singleplayer these need cheats; open the world to LAN with cheats on to use them.

### The playtest and the Minecraft MCP server
`tools/playtest.py` plays the whole story through and checks each step: the raft, the current, Bruce, a real cast
catching a barrel and reeling it in, the island arriving in slices, setting down and throwing the anchor, mooring,
the island as blocks with its loot box, breaking the post, casting off, and the island drifting away.

Its player is the bot of the Minecraft (Java) MCP server,
[yuniko-software/minecraft-mcp-server](https://github.com/yuniko-software/minecraft-mcp-server), which
`tools/mcp_bot.py` runs and keeps in the game. That server has no tool to use an item or click an entity, so a click
on the anchor's post is written into the record the post keeps of who clicked it, and casting is done by a second
player, Fisher (`tools/fisher.cjs`), a plain mineflayer client.

mineflayer speaks Java Edition up to 26.1, so the bot plays on a 26.1 server. ViaProxy 3.4.14 can put it on 26.3,
but the server kicks it a second after it joins for an invalid movement packet, so that route does not work yet.

```bash
python tools/server.py ../minecraft-java-server/26.1 --version 26.1 --port 25567 --rcon-port 25576 --link
(cd ../minecraft-java-server/26.1 && java -jar server.jar nogui) &
python tools/mcp_bot.py serve --port 25567 &
python tools/playtest.py --rcon-port 25576 --game-port 25567
```

`--headless` plays the same story with no players at all, calling the pack's own functions where a player would
act, so it runs on any version. The Test workflow runs it on a fresh 26.1, 26.2 and 26.3 server for every push, and
checks the server's log for data pack errors and the generated functions for being up to date.

## Trailer
`tools/trailer.py` films the trailer on the local server with the Java client on this Mac, the way minecRAFT-bedrock's
does with Bedrock: commands over RCON, real keys and clicks through `tools/client_drive.py` (macOS input events),
and the picture and the game's own sound recorded together by `tools/sck_capture.py` (ScreenCaptureKit, filtered to
the Minecraft client, so nothing else on the Mac is heard). The camera is the player spectating an invisible item
display moved a tick at a time along an eased path, which the client glides; a mannequin wearing the player's skin
stands in for them on the raft.

```bash
python tools/trailer.py prep            # morning, clear, no island, the anchor set down on the raft for real
python tools/trailer.py shot open       # one shot into trailer/takes/open.mp4 (the shots are listed in the script)
python tools/trailer.py moor            # bring the island in and anchor it again, to refilm the moored shots
python tools/trailer.py reset           # the player's body, HUD and the game rules back
python tools/trailer_cut.py             # cuts trailer/minecRAFT-trailer.mp4 from trailer/edit.json and trailer/titles.json
```

The client runs fullscreen with music off and the HUD hidden (F1), so the takes are filmed while nobody is using the
Mac. The cut uses the trailer skill's `titles.py` and `assemble.py`: shots measured in beats of the music, the game's
sound under it, the music ducked beneath that, levelled to -14 LUFS. The music (A Beautiful Discovery, from the
Fantasy Adventure & Exploration Music pack) and the game's fonts are copied into the git-ignored `trailer/takes/`.

## Releasing
Pushing a tag that starts with `v` (for example `git tag v1.0.0 && git push origin v1.0.0`) runs the Release workflow
in `.github/workflows/release.yml`, which builds the world with `tools/build_world.py` and attaches `minecRAFT.zip` to
a GitHub Release.

To build it locally, run `python tools/build_world.py`. It writes `build/minecRAFT.zip`, which git ignores.
