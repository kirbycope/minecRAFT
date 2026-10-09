# Clicked on top: thrown off the first edge of the plank underneath with no plank beyond it (north, west, east,
# south), north if there is none. Yaw 0 is south, 90 west, 180 north, 270 east.
execute unless block ~ ~-1 ~-1 #minecraft:planks run return run function raft:anchor/set_down {yaw:180}
execute unless block ~-1 ~-1 ~ #minecraft:planks run return run function raft:anchor/set_down {yaw:90}
execute unless block ~1 ~-1 ~ #minecraft:planks run return run function raft:anchor/set_down {yaw:270}
execute unless block ~ ~-1 ~1 #minecraft:planks run return run function raft:anchor/set_down {yaw:0}
function raft:anchor/set_down {yaw:180}
