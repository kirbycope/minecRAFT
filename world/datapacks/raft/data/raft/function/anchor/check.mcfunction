# Once a second while an anchor is set down: a post broken some other way than by hitting it (from below, by an
# explosion) destroys the anchor too, and a lead someone untied from the anchor is tied again.
execute if score #anchor raft.state matches 1.. run function raft:anchor/check_at with storage raft:anchor post
