#!/usr/bin/env python3
"""Test frame simulation with detailed timing of each section"""

import time
from match_simulation_engine_v2 import Match, create_sample_teams

print("[TEST] Detailed Frame Timing Analysis")
print("=" * 80)

home, away = create_sample_teams()
match = Match(home, away)

print(f"Setup complete:")
print(f"  - Home: {len(home.players)} players")
print(f"  - Away: {len(away.players)} players")
print()

all_players = home.players + away.players
for player in all_players:
    match.spatial_grid.add_agent(player, player.x, player.y)

if all_players:
    match.ball_holder = all_players[0]
    match.ball_holder.has_ball = True
    match.ball_possession = "Home"

# Run simulate_frame and observe the timing prints
print("Running simulate_frame()...")
print("Watch for timing breakdown:")
print("=" * 80)

start = time.perf_counter()

match.current_frame = 0
match.current_minute = 0
match.simulate_frame(dt=1.0/60.0)

end = time.perf_counter()
total_ms = (end - start) * 1000

print()
print("=" * 80)
print(f"TOTAL FRAME TIME: {total_ms:.2f}ms")
print("=" * 80)
