# Removes the island, entities or blocks, so another can be brought.
#   function raft:island/clear
execute as @e[type=minecraft:block_display,tag=island.root] run function raft:island/remove_slice
kill @e[type=minecraft:block_display,tag=island]
execute if score #island raft.state matches 2 run function raft:island/clear_at_x
scoreboard players set #island raft.state 0
