execute if block ~ ~ ~ minecraft:oak_fence align xyz positioned ~0.5 ~ ~0.5 run return run function raft:anchor/found
scoreboard players add #ray raft.tmp 1
execute if score #ray raft.tmp matches ..140 positioned ^ ^ ^0.05 run function raft:anchor/ray
