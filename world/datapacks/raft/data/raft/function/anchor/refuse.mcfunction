function raft:anchor/unplace
execute unless entity @s[gamemode=creative] run function raft:anchor/give
$title @s actionbar "$(message)"
