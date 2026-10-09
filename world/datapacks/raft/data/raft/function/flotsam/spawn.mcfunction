# One piece of flotsam at x: a random kind, somewhere across the stream, turned any which way, bobbing up while
# half the others bob down. While an island is about, flotsam keeps to the far side of the raft, so none of it floats
# through the rock. Nothing is spawned into an unloaded chunk: the game would save it there unseen, where it neither
# drifts nor counts toward the 30.
#   function raft:flotsam/spawn {x:-32}
$data modify storage raft:tmp spawn set value {x:$(x),bob:"bob.a"}
execute store result storage raft:tmp spawn.yaw float 1 run random value 0..359
execute if score #island raft.state matches 0 store result storage raft:tmp spawn.z double 0.01 run random value -300..2100
execute unless score #island raft.state matches 0 store result storage raft:tmp spawn.z double 0.01 run random value -500..700
execute store result score #kind raft.tmp run random value 0..1
execute if score #kind raft.tmp matches 1 run data modify storage raft:tmp spawn.bob set value "bob.b"
execute store result score #kind raft.tmp run random value 1..11
execute if score #kind raft.tmp matches 1 run function raft:flotsam/summon/barrel with storage raft:tmp spawn
execute if score #kind raft.tmp matches 2..5 run function raft:flotsam/summon/plank with storage raft:tmp spawn
execute if score #kind raft.tmp matches 6..8 run function raft:flotsam/summon/palm_leaf with storage raft:tmp spawn
execute if score #kind raft.tmp matches 9..11 run function raft:flotsam/summon/plastic with storage raft:tmp spawn
