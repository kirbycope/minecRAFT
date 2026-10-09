# Positioned at the hut's chest as the island sinks: what is left in it floats out onto the water.
setblock ~ ~ ~ minecraft:air destroy
kill @e[type=minecraft:item,distance=..2,nbt={Item:{id:"minecraft:chest"}}]
