# Casting off: once the anchor is gone, what is left of the island (every block still as it was placed) goes back to
# being entities, the blocks go back to ocean, and the island drifts on downstream. It waits for its chunks.
execute if score #anchor raft.state matches 2 run return fail
execute store result storage raft:island x int 0.001 run scoreboard players get #island_x raft.state
function raft:island/cast_off with storage raft:island
