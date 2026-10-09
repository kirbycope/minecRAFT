# Left alone a dolphin swims out of loaded range and is never seen again, so Bruce is steered back toward the raft
# while he is more than 12 blocks from it.
execute as @e[type=minecraft:dolphin,tag=raft.bruce,x=9,y=105,z=9,distance=12..64] at @s facing 9 ~ 9 run tp @s ^ ^ ^0.08
