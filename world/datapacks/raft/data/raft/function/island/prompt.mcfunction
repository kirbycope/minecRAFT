# Every five seconds while the island is within 14 blocks of alongside, to whoever could still anchor.
scoreboard players set #prompt raft.tmp 0
execute if score #anchor raft.state matches 2 run return fail
execute unless score #island_x raft.state matches -21999..5999 run return fail
execute as @a if function raft:anchor/has run title @s actionbar "An island! Throw your anchor to stop here."
