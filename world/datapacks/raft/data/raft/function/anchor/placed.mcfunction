# Raft's Throwable Anchor; https://raft.fandom.com/wiki/Throwable_Anchor
#
# Use the item on the raft to set it down: a fence post on the raft with the anchor tied to it by a lead. Use the
# post (or the anchor) to throw the anchor into the water, which anchors the raft. Like Raft's, it works once:
# breaking the post destroys it, anchor and all, and the raft drifts again.
#
# As and at the player who has just placed the anchor's fence post. Placing a block does not say where, so a ray
# from their eyes finds the post: it lies between them and the face they clicked.
scoreboard players set #ray raft.tmp 0
execute anchored eyes positioned ^ ^ ^ run function raft:anchor/ray
