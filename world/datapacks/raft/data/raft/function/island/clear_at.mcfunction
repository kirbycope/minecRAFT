# Also removes island blocks left standing with the island's origin at x (a world where the island became blocks
# and the state was lost).
#   function raft:island/clear_at {x:-8}
$execute positioned $(x) 105 10 run function raft:island/generated/sink
