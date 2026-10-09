# With the raft's chunk unloaded (nobody near) the island's entities cannot move, so neither does the island.
execute unless loaded 8 105 8 run return fail

# Slices come into being as their downstream edge comes within 56 blocks upstream of the raft (x 8).
scoreboard players operation #edge raft.tmp = #island_x raft.state
scoreboard players add #edge raft.tmp 48000
execute if score #slice_next raft.state < #slices raft.state run function raft:island/generated/spawn_next
execute if score #slice_next raft.state matches 1.. unless entity @e[type=minecraft:block_display,tag=island.root] run return run function raft:island/gone

# The current carries it 0.04 blocks a tick. With the raft anchored it has stopped too: one that is all here
# settles onto the next whole block and becomes solid there; one still coming over the horizon just waits.
scoreboard players operation #frac raft.tmp = #island_x raft.state
scoreboard players operation #frac raft.tmp %= #1000 raft.tmp
scoreboard players set #step raft.tmp 1
execute if score #anchor raft.state matches 2 unless score #slice_next raft.state >= #slices raft.state run scoreboard players set #step raft.tmp 0
execute if score #anchor raft.state matches 2 if score #frac raft.tmp matches 0 run scoreboard players set #step raft.tmp 0
execute if score #step raft.tmp matches 1 run function raft:island/move
execute if score #anchor raft.state matches 2 if score #slice_next raft.state >= #slices raft.state if score #frac raft.tmp matches 0 run return run function raft:island/moor

# Gone 56 blocks past the raft.
execute as @e[type=minecraft:block_display,tag=island.root,x=64,y=-64,z=-30000000,dx=30000000,dy=400,dz=60000000] run function raft:island/remove_slice

scoreboard players add #prompt raft.tmp 1
execute if score #prompt raft.tmp matches 100.. run function raft:island/prompt
