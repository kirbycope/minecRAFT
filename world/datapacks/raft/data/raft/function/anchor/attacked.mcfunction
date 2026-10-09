# Who hit it is read from the record before it is cleared: on attacker is that record.
execute on attacker run function raft:anchor/hit
data remove entity @s attack
