# Whether the executing player can still anchor: one is set down on the raft and not yet thrown, or they carry one.
execute if score #anchor raft.state matches 1 run return 1
execute if items entity @s container.* minecraft:oak_fence[minecraft:custom_data~{raft_anchor:true}] run return 1
execute if items entity @s weapon.offhand minecraft:oak_fence[minecraft:custom_data~{raft_anchor:true}] run return 1
return fail
