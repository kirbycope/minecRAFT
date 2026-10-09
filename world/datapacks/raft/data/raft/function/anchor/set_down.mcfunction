# The post, the anchor beside it on the side it will be thrown from, and the lead between them. Where it is goes into
# storage raft:anchor post, as whole blocks, read from a marker at the block's corner.
setblock ~ ~ ~ minecraft:oak_fence
scoreboard players set #anchor raft.state 1
scoreboard players set #throw raft.state 0
$data modify storage raft:anchor post set value {yaw:$(yaw)}
execute align xyz run summon minecraft:marker ~ ~ ~ {Tags:["raft.where"]}
execute store result storage raft:anchor post.x int 1 run data get entity @e[type=minecraft:marker,tag=raft.where,limit=1] Pos[0]
execute store result storage raft:anchor post.y int 1 run data get entity @e[type=minecraft:marker,tag=raft.where,limit=1] Pos[1]
execute store result storage raft:anchor post.z int 1 run data get entity @e[type=minecraft:marker,tag=raft.where,limit=1] Pos[2]
kill @e[type=minecraft:marker,tag=raft.where]
function raft:anchor/rig with storage raft:anchor post
playsound minecraft:block.chain.place block @a ~ ~ ~ 1 0.8
title @s actionbar "Use the post to throw the anchor."
