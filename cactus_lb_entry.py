# Leaderboards.Cactus entry: farm 33,554,432 cacti, then end the program.
#
# The leaderboard starts with everything unlocked (a 32x32 field, 32 drones), pumpkins and lots of
# power. cactus.py's mesh sort needs one drone per 2x4 block, which is 32 drones on a 16x16 field,
# so the field is shrunk first; cactus.py reads the size when it is imported. A 16x16 harvest at
# full cactus upgrades is 2,097,152 cacti, so the goal takes 16 harvests.
#
# A leaderboard run only finishes when every drone has returned, so cactus.run() is given the goal
# and all drones stop together once it is reached.

GOAL = 33554432

set_world_size(16)

import cactus

cactus.run(GOAL)
