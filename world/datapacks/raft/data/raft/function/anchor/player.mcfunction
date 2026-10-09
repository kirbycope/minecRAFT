# As and at each player, every tick. A fence placed by someone who held an anchor a tick ago was the anchor: the
# oak fence use statistic says a fence went down, and the hands as they were before it say which kind.
execute if score @s raft.fence matches 1.. run function raft:anchor/fence_used
scoreboard players set @s raft.held 0
execute if items entity @s weapon.mainhand minecraft:oak_fence[minecraft:custom_data~{raft_anchor:true}] run scoreboard players add @s raft.held 1
execute if items entity @s weapon.offhand minecraft:oak_fence[minecraft:custom_data~{raft_anchor:true}] run scoreboard players add @s raft.held 2
