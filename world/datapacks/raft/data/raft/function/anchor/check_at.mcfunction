$execute unless loaded $(x) $(y) $(z) run return fail
$execute unless block $(x) $(y) $(z) minecraft:oak_fence run return run function raft:anchor/destroy
$execute as @e[type=minecraft:frog,tag=raft.carrier] unless data entity @s leash run data modify entity @s leash set value [I;$(x),$(y),$(z)]
$kill @e[type=minecraft:item,x=$(x),y=$(y),z=$(z),distance=..10,nbt={Item:{id:"minecraft:lead"}}]
