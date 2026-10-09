# Takes the fence post here away again, leaving what was there before it.
execute if block ~ ~ ~ minecraft:oak_fence[waterlogged=true] run return run setblock ~ ~ ~ minecraft:water
execute if block ~ ~ ~ minecraft:oak_fence run setblock ~ ~ ~ minecraft:air
