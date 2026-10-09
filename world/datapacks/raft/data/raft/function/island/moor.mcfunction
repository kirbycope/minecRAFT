# The island stops alongside the raft and becomes real blocks, placed only where there is still ocean, so nothing a
# player built is overwritten. The entities go in the same tick, so it never flickers.
execute store result storage raft:island x int 0.001 run scoreboard players get #island_x raft.state
function raft:island/moor_at with storage raft:island
