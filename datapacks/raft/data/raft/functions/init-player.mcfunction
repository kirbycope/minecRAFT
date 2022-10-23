# Tag player so this only runs for them once
tag @a[tag=!init] add init

# Give player a fishing rod
give @s minecraft:fishing_rod

summon minecraft:item ~2 ~ ~2 {Item:{id:"minecraft:jungle_planks",Count:1},Tags:[flotsam]}
summon minecraft:item ~-2 ~ ~-2 {Item:{id:"minecraft:jungle_planks",Count:1},Tags:[flotsam]}

summon minecraft:item ~3 ~ ~-3 {Item:{id:"minecraft:jungle_leaves",Count:1},Tags:[flotsam]}
summon minecraft:item ~3 ~ ~-3 {Item:{id:"minecraft:jungle_leaves",Count:1},Tags:[flotsam]}
