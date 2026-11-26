# Leaderboards.Cactus entry: farm 33,554,432 cacti, then end the program.
#
# The leaderboard starts with everything unlocked (a 32x32 field, 32 drones), pumpkins and lots of
# power. cactus.py sorts the whole 32x32 field with one drone per 2x16 block, split by wall
# columns and rows every 8 tiles into sixteen regions of about 8x8. One harvest of that field is
# 22,632,992 cacti, so the goal takes two harvests (about 24.9s simulated). A 16x16 field needed 16.
#
# A leaderboard run only finishes when every drone has returned, so cactus.run() is given the goal
# and all drones stop together once it is reached.

GOAL = 33554432

import cactus

cactus.run(GOAL)
