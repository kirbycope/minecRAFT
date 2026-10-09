# The first island encounter: Raft's Small Island 1 (tools/island.py builds it into island/generated/).
#
# The island comes into sight upstream as display entities, a slice at a time as each comes within 56 blocks,
# drifting toward the raft with the current exactly as the flotsam does. Each slice is an empty block display
# carrying the rest as passengers, so the whole island moves with one teleport per slice. Left alone it drifts past
# and away. Throw the anchor while it is alongside and the island stops on whole-block coordinates and turns into
# real blocks: rock to climb, palms to chop, ore to mine, a loot box in the hut. When the anchor is destroyed the
# raft drifts again: whatever is left of the island turns back into entities and drifts away.
#
# #island raft.state: 0 none, 1 drifting (entities), 2 moored (blocks). #island_x is the island's origin x in
# thousandths of a block; its origin is at y 105 (the ocean's top layer) and z 10.
execute if score #island raft.state matches 0 run return run function raft:island/wait
execute if score #island raft.state matches 1 run return run function raft:island/drift
execute if score #island raft.state matches 2 run function raft:island/moored
