# A player's first time on the raft: a number to tell their hooks apart, a fishing rod and a Throwable Anchor.
# Raft has you craft your first anchor; here you start with one so the first island can be visited.
tag @s add raft.init
scoreboard players add #next raft.pid 1
scoreboard players operation @s raft.pid = #next raft.pid
give @s minecraft:fishing_rod
function raft:anchor/give
recipe give @s raft:throwable_anchor
