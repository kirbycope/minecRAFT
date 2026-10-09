# Called by island/generated/spawn_next with the slice's number.
$data modify storage raft:island n set value $(n)
execute store result storage raft:island x double 0.001 run scoreboard players get #island_x raft.state
execute store result score #ok raft.tmp run function raft:island/spawn_slice_at with storage raft:island
execute if score #ok raft.tmp matches 1 run scoreboard players add #slice_next raft.state 1
