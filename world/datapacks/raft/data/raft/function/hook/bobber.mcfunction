# As and at a fishing hook. Anything floating within 1.6 blocks of it is caught and rides on the line.
execute unless score @s raft.hook matches 1.. run function raft:hook/new
scoreboard players operation #hook raft.tmp = @s raft.hook
scoreboard players operation #owner raft.tmp = @s raft.owner
execute as @e[type=#raft:display,tag=flotsam,tag=!hooked,distance=..1.6] run function raft:hook/catch
execute as @e[type=#raft:display,tag=hooked] if score @s raft.hook = #hook raft.tmp run function raft:hook/carry
