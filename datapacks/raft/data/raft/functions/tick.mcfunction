# Initialize new players
execute as @a[tag=!init] run function raft:init-player

# Summon flotsam
summon minecraft:item ~1 ~ ~ {Item:{id:"minecraft:jungle_planks",Count:1},NoGravity:1b,Tags:[flotsam]}
summon minecraft:item ~2 ~ ~ {Item:{id:"minecraft:jungle_planks",Count:1},NoGravity:1b,Tags:[flotsam]}
summon minecraft:item ~3 ~ ~ {Item:{id:"minecraft:jungle_planks",Count:1},NoGravity:1b,Tags:[flotsam]}
summon minecraft:item ~ ~ ~1 {Item:{id:"minecraft:jungle_planks",Count:1},NoGravity:1b,Tags:[flotsam]}
summon minecraft:item ~ ~ ~2 {Item:{id:"minecraft:jungle_planks",Count:1},NoGravity:1b,Tags:[flotsam]}
summon minecraft:item ~ ~ ~3 {Item:{id:"minecraft:jungle_planks",Count:1},NoGravity:1b,Tags:[flotsam]}

spreadplayers  ~ ~ 4 1 @a[tag=flotsam]
