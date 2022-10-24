# Tag player so this only runs for them once
tag @a[tag=!init] add init

# Give player a fishing rod
give @s minecraft:fishing_rod

## https://raft.fandom.com/wiki/Flotsam ##

# [Barrel]

# [Palm Leaf] Jungle Leaves
summon minecraft:item ~3 ~ ~-3 {Item:{id:"minecraft:jungle_leaves",Count:1},Tags:[flotsam]}
summon minecraft:item ~-3 ~ ~3 {Item:{id:"minecraft:jungle_leaves",Count:1},Tags:[flotsam]}

# [Plank] Plank
summon minecraft:item ~2 ~ ~2 {Item:{id:"minecraft:jungle_planks",Count:1},Tags:[flotsam]}
summon minecraft:item ~-2 ~ ~-2 {Item:{id:"minecraft:jungle_planks",Count:1},Tags:[flotsam]}

# [Plastic] Sugar Cane
summon minecraft:item ~5 ~ ~ {Item:{id:"minecraft:sugar_cane",Count:1},Tags:[flotsam]}
summon minecraft:item ~-5 ~ ~ {Item:{id:"minecraft:sugar_cane",Count:1},Tags:[flotsam]}
