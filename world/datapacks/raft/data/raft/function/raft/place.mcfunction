# The 2x2 raft, once, as soon as its chunk is loaded, and the whole stream at once so a new world starts with
# flotsam already in reach.
fill 8 105 8 9 105 9 minecraft:jungle_planks
scoreboard players set #raft_placed raft.state 1
function raft:flotsam/spawn {x:-32}
function raft:flotsam/spawn {x:-25.3}
function raft:flotsam/spawn {x:-18.7}
function raft:flotsam/spawn {x:-12}
function raft:flotsam/spawn {x:-5.3}
function raft:flotsam/spawn {x:1.3}
function raft:flotsam/spawn {x:8}
function raft:flotsam/spawn {x:14.7}
function raft:flotsam/spawn {x:21.3}
function raft:flotsam/spawn {x:28}
function raft:flotsam/spawn {x:34.7}
function raft:flotsam/spawn {x:41.3}
