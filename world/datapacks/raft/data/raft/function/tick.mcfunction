execute if score #raft_placed raft.state matches 0 if loaded 8 105 8 run function raft:raft/place
execute as @a[tag=!raft.init] run function raft:player/init

function raft:hook/tick
function raft:flotsam/tick
function raft:island/tick
function raft:anchor/tick
function raft:bruce/tick
