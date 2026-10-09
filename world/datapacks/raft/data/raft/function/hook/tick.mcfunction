# Hooks: catch what a hook lands beside, carry it while the line is out, deliver it when the line comes in.
tag @e[type=#raft:display,tag=hooked] remove hook.held
execute as @e[type=minecraft:fishing_bobber] at @s run function raft:hook/bobber
execute as @e[type=#raft:display,tag=hooked,tag=!hook.held] at @s run function raft:hook/reel_in
