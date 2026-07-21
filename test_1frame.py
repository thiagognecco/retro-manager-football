#!/usr/bin/env python3
"""Test 1 single frame to see which operation is slow"""

import time
from match_simulation_engine_v2 import Match, create_sample_teams

print("[TEST] Starting 1-frame test with detailed timing...")
print("=" * 80)

home, away = create_sample_teams()
match = Match(home, away)

print(f"Setup complete:")
print(f"  - Home team: {len(home.players)} players")
print(f"  - Away team: {len(away.players)} players")
print(f"  - Spatial grid: {match.spatial_grid.width}x{match.spatial_grid.height}m")
print()

# Add players to spatial grid
all_players = home.players + away.players
for player in all_players:
    match.spatial_grid.add_agent(player, player.x, player.y)

# Set one player as ball holder
if all_players:
    match.ball_holder = all_players[0]
    match.ball_holder.has_ball = True
    match.ball_possession = "Home"

print("Running 1 frame simulation...")
print("=" * 80)

start = time.perf_counter()
match.current_frame = 0
match.current_minute = 0
match.simulate_frame(dt=1.0/60.0)
end = time.perf_counter()

total_ms = (end - start) * 1000

print()
print("=" * 80)
print(f"SINGLE FRAME TIME: {total_ms:.2f}ms")
print("=" * 80)

if total_ms < 10:
    print(f"[GOOD] Frame time {total_ms:.2f}ms (target: <2ms)")
else:
    print(f"[SLOW] Frame time {total_ms:.2f}ms - BOTTLENECK FOUND!")
    print(f"Check the timing breakdown printed above")
