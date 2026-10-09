# As a player who used the post: throw the anchor, and the raft is anchored.
execute unless score #anchor raft.state matches 1 run return fail
scoreboard players set #anchor raft.state 2
scoreboard players set #throw raft.state 1
title @s actionbar "Anchor down. The raft has stopped."
