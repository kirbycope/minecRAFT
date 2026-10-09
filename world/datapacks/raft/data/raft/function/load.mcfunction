# minecRAFT: Raft but in Minecraft.
#
# The raft never moves. The ocean is the flat world's water, endless and the same everywhere, so the current is
# shown by moving everything floating in it past the raft instead: flotsam is block and item display entities,
# teleported a little downstream every tick, which the client glides between. A fishing hook that lands next to
# a piece of flotsam carries it, and reeling in gives its loot.
#
# The tuning:
#   the raft          x 8..9, z 8..9, in the ocean's top layer (y 105)        raft/place, setworldspawn below
#   the current       0.04 blocks a tick east (0.8 a second)                  flotsam/drift, island/tick
#   the stream        from x -32 to x 48, 12 blocks either side of the raft  flotsam/spawn, flotsam/tick
#   the hook's reach  1.6 blocks                                              hook/bobber
#   Bruce's leash     12 blocks from the raft                                 bruce
#   the island        passes at z 10, alongside at x -8, from x -92          island/start
#   the anchor        thrown 3 blocks out, sinks to y 102                     anchor/arc

scoreboard objectives add raft.state dummy
scoreboard objectives add raft.tmp dummy
scoreboard objectives add raft.cover dummy
scoreboard objectives add raft.pid dummy
scoreboard objectives add raft.hook dummy
scoreboard objectives add raft.owner dummy
scoreboard objectives add raft.fence minecraft.used:minecraft.oak_fence
scoreboard objectives add raft.held dummy

# A new world: nothing placed, no island seen, the first one due a couple of minutes in.
execute unless score #raft_placed raft.state matches 0.. run scoreboard players set #raft_placed raft.state 0
execute unless score #island raft.state matches 0.. run scoreboard players set #island raft.state 0
execute unless score #island1_seen raft.state matches 0.. run scoreboard players set #island1_seen raft.state 0
execute unless score #island1_due raft.state matches 0.. run scoreboard players set #island1_due raft.state 2400
execute unless score #anchor raft.state matches 0.. run scoreboard players set #anchor raft.state 0
execute unless score #chest_filled raft.state matches 0.. run scoreboard players set #chest_filled raft.state 0
execute unless score #throw raft.state matches 0.. run scoreboard players set #throw raft.state 0

setworldspawn 9 106 9
gamerule minecraft:respawn_radius 0

scoreboard players set #1000 raft.tmp 1000
function raft:island/generated/constants

schedule function raft:second 20t replace
