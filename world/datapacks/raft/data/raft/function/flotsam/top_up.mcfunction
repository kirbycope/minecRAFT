scoreboard players set #spawn_wait raft.tmp 0
execute store result score #count raft.tmp if entity @e[type=#raft:display,tag=flotsam,tag=!hooked]
execute if score #count raft.tmp matches ..29 run function raft:flotsam/spawn {x:-32}
