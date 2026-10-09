# Bruce, the shark of the original, is a dolphin here as he was in the first Java map. A new Bruce is spawned
# whenever someone is on the raft and none is near it.
execute unless entity @a[x=9,y=105,z=9,distance=..48] run return fail
execute if entity @e[type=minecraft:dolphin,tag=raft.bruce,x=9,y=105,z=9,distance=..64] run return fail
execute if loaded 17 104 17 run summon minecraft:dolphin 17 104 17 {CustomName:"Bruce",PersistenceRequired:1b,Silent:1b,Tags:["raft.bruce"]}
