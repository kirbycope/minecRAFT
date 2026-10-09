# Every slice has drifted out of range downstream.
execute if score #slice_next raft.state >= #slices raft.state run scoreboard players set #island raft.state 0
