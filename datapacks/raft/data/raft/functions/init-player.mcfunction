# Tag player so this only runs for them once
tag @a[tag=!init] add init

# Give player a fishing rod
give @s minecraft:fishing_rod

# Summon flotsam
summon minecraft:item ~1 ~ ~ {Item:{id:"minecraft:jungle_planks",Count:1},NoGravity:1b,Tags:[flotsam]}
summon minecraft:item ~2 ~ ~ {Item:{id:"minecraft:jungle_planks",Count:1},NoGravity:1b,Tags:[flotsam]}
summon minecraft:item ~3 ~ ~ {Item:{id:"minecraft:jungle_planks",Count:1},NoGravity:1b,Tags:[flotsam]}
summon minecraft:item ~ ~ ~1 {Item:{id:"minecraft:jungle_planks",Count:1},NoGravity:1b,Tags:[flotsam]}
summon minecraft:item ~ ~ ~2 {Item:{id:"minecraft:jungle_planks",Count:1},NoGravity:1b,Tags:[flotsam]}
summon minecraft:item ~ ~ ~3 {Item:{id:"minecraft:jungle_planks",Count:1},NoGravity:1b,Tags:[flotsam]}

spreadplayers  ~ ~ 4 1 @e[tag=flotsam]
