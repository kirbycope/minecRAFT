# The first island turns up a couple of minutes (2400 ticks with someone online) into a new world, once.
execute if score #island1_seen raft.state matches 1 run return fail
execute unless entity @a run return fail
scoreboard players remove #island1_due raft.state 1
execute if score #island1_due raft.state matches ..0 run function raft:island/start {x:-92}
