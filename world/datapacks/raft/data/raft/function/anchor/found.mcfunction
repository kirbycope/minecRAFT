# At the middle of the bottom of the post just placed. It belongs on top of a plank; the anchor is thrown off the
# side that was clicked, or off the nearest edge when the top was.
execute unless score #anchor raft.state matches 0 run return run function raft:anchor/refuse {message:"There is already an anchor on the raft."}
execute if block ~ ~-1 ~ #minecraft:planks run return run function raft:anchor/on_top
# Against the side of a plank: the post moves up onto that plank, and that side is where the anchor goes.
execute if block ~1 ~ ~ #minecraft:planks if block ~1 ~1 ~ #raft:ocean run return run function raft:anchor/from_side {dx:1,dz:0,yaw:90}
execute if block ~-1 ~ ~ #minecraft:planks if block ~-1 ~1 ~ #raft:ocean run return run function raft:anchor/from_side {dx:-1,dz:0,yaw:270}
execute if block ~ ~ ~1 #minecraft:planks if block ~ ~1 ~1 #raft:ocean run return run function raft:anchor/from_side {dx:0,dz:1,yaw:180}
execute if block ~ ~ ~-1 #minecraft:planks if block ~ ~1 ~-1 #raft:ocean run return run function raft:anchor/from_side {dx:0,dz:-1,yaw:0}
function raft:anchor/refuse {message:"Set the anchor down on the raft."}
