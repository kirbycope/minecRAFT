# Tag player so this only runs for them once
tag @a[tag=!init] add init

# Give player a fishing rod
give @s minecraft:fishing_rod

summon minecraft:item ~2 ~-0.5 ~2 {Item:{id:"minecraft:jungle_planks",Count:1},NoGravity:1b,Tags:[flotsam]}
summon minecraft:item ~2 ~-0.5 ~3 {Item:{id:"minecraft:jungle_planks",Count:1},NoGravity:1b,Tags:[flotsam]}
summon minecraft:item ~2 ~-0.5 ~4 {Item:{id:"minecraft:jungle_planks",Count:1},NoGravity:1b,Tags:[flotsam]}
