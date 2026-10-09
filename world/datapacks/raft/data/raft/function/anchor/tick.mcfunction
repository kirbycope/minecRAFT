# The post's interaction box remembers who last used it and who last hit it.
execute as @e[type=minecraft:interaction,tag=raft.post] if data entity @s interaction run function raft:anchor/interacted
execute as @e[type=minecraft:interaction,tag=raft.post] if data entity @s attack run function raft:anchor/attacked
execute as @a at @s run function raft:anchor/player

# The throw: an arc out over the water, then down through it, from the post toward the side it was set down on.
execute unless score #throw raft.state matches 1.. run return fail
execute as @e[type=minecraft:frog,tag=raft.carrier,limit=1] at @e[type=minecraft:interaction,tag=raft.post,limit=1] positioned ~ ~0.5 ~ run function raft:anchor/generated/arc
scoreboard players add #throw raft.state 1
execute if score #throw raft.state matches 43.. run scoreboard players set #throw raft.state 0
