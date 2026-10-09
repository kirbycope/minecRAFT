# Flotsam whose hook has gone, because the line was reeled in: its loot goes to whoever cast it (or, failing
# that, the nearest player, who cast it in any but the most crowded raft).
scoreboard players operation #owner raft.tmp = @s raft.owner
tag @a remove raft.receiver
execute as @a if score @s raft.pid = #owner raft.tmp run tag @s add raft.receiver
execute unless entity @a[tag=raft.receiver] run tag @p[distance=..40] add raft.receiver
execute if entity @s[tag=flotsam.barrel] run loot give @a[tag=raft.receiver,limit=1] loot raft:flotsam/barrel
execute if entity @s[tag=flotsam.plank] run loot give @a[tag=raft.receiver,limit=1] loot raft:flotsam/plank
execute if entity @s[tag=flotsam.palm_leaf] run loot give @a[tag=raft.receiver,limit=1] loot raft:flotsam/palm_leaf
execute if entity @s[tag=flotsam.plastic] run loot give @a[tag=raft.receiver,limit=1] loot raft:flotsam/plastic
execute if entity @a[tag=raft.receiver] run playsound minecraft:entity.item.pickup player @a ~ ~ ~ 0.6 1.2
tag @a remove raft.receiver
kill @s
