# Who clicked is read from the record before it is cleared: on target is that record.
execute on target run function raft:anchor/use
data remove entity @s interaction
