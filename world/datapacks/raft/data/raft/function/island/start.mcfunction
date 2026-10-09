# Brings the island from x (a whole number): -92 is just out of range, over the horizon; -16 is a few seconds
# upstream of alongside (x -8, where the raft lies beside the middle of the main rock).
#   function raft:island/start {x:-92}
execute unless score #island raft.state matches 0 run return fail
scoreboard players set #island raft.state 1
$scoreboard players set #island_x raft.state $(x)000
scoreboard players set #slice_next raft.state 0
scoreboard players set #island1_seen raft.state 1
scoreboard players set #chest_filled raft.state 0
kill @e[type=#raft:display,tag=flotsam,tag=!hooked,x=-30000000,y=-64,z=7,dx=60000000,dy=400,dz=30000000]
