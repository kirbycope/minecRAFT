$execute positioned $(x) 105 10 unless function raft:island/generated/loaded run return fail
$execute positioned $(x) 105 10 run function raft:island/generated/place
execute as @e[type=minecraft:block_display,tag=island.root] run function raft:island/remove_slice
scoreboard players set #island raft.state 2
