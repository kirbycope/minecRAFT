# A hook just cast: a number of its own, and the number of the player who cast it. A fishing hook does not keep its
# owner where a command can see it (execute on owner finds no one), so the caster is the nearest player holding a
# rod, within reach of where a hook is a tick after it is cast.
scoreboard players add #next raft.hook 1
scoreboard players operation @s raft.hook = #next raft.hook
scoreboard players set #owner raft.tmp 0
execute as @a[distance=..5] if items entity @s weapon.* minecraft:fishing_rod run tag @s add raft.rod
execute as @p[tag=raft.rod] run scoreboard players operation #owner raft.tmp = @s raft.pid
tag @a remove raft.rod
scoreboard players operation @s raft.owner = #owner raft.tmp
