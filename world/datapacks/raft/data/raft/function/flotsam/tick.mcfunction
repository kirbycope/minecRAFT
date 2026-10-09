# The current: everything not on a hook drifts east, bobbing, and is gone once it is 40 blocks past the raft.
scoreboard players add #bob raft.tmp 1
execute if score #bob raft.tmp matches 60.. run scoreboard players set #bob raft.tmp 0
execute if score #bob raft.tmp matches ..29 as @e[type=#raft:display,tag=bob.a,tag=!hooked] at @s run tp @s ~0.04 ~0.002 ~
execute if score #bob raft.tmp matches ..29 as @e[type=#raft:display,tag=bob.b,tag=!hooked] at @s run tp @s ~0.04 ~-0.002 ~
execute if score #bob raft.tmp matches 30.. as @e[type=#raft:display,tag=bob.a,tag=!hooked] at @s run tp @s ~0.04 ~-0.002 ~
execute if score #bob raft.tmp matches 30.. as @e[type=#raft:display,tag=bob.b,tag=!hooked] at @s run tp @s ~0.04 ~0.002 ~
kill @e[type=#raft:display,tag=flotsam,tag=!hooked,x=48,y=-64,z=-30000000,dx=30000000,dy=400,dz=60000000]

# A new piece upstream every second while there are fewer than 30.
scoreboard players add #spawn_wait raft.tmp 1
execute if score #spawn_wait raft.tmp matches 20.. run function raft:flotsam/top_up
