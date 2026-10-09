$execute positioned $(x) 105 10 unless function raft:island/generated/loaded run return fail
$execute positioned $(x) 105 10 run function raft:island/generated/lift
$execute positioned $(x) 105 10 run function raft:island/generated/sink
scoreboard players operation #slice_next raft.state = #slices raft.state
scoreboard players set #island raft.state 1
