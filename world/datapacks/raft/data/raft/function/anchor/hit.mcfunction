# As a player who hit the post: it is single use, as in Raft.
execute if score #anchor raft.state matches 0 run return fail
function raft:anchor/destroy
title @s actionbar "The anchor is gone, and the raft drifts on."
