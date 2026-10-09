# The post comes down and the anchor and its lead are gone with it. The frog is dropped out of the world rather than
# killed, so it leaves no puff of smoke; the leads the game drops as the lead breaks are swept up.
scoreboard players set #anchor raft.state 0
scoreboard players set #throw raft.state 0
execute as @e[type=minecraft:frog,tag=raft.carrier] on passengers run kill @s
execute as @e[type=minecraft:frog,tag=raft.carrier] at @s run function raft:anchor/drop_frog
execute at @e[type=minecraft:interaction,tag=raft.post] run function raft:anchor/unplace
execute at @e[type=minecraft:interaction,tag=raft.post] run kill @e[type=minecraft:leash_knot,distance=..1.5]
kill @e[type=minecraft:interaction,tag=raft.post]
function raft:anchor/sweep with storage raft:anchor post
schedule function raft:anchor/sweep_later 2t replace
