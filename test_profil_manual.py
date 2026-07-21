#!/usr/bin/env python3
"""Manually profile where time is being spent"""

import time
import sys

# Monkey-patch nearby_agents to count calls
from spatial_hash_grid import SpatialHashGrid
original_nearby = SpatialHashGrid.nearby_agents

call_counts = {}
call_times = {}

def patched_nearby(self, x, y, radius):
    global call_counts, call_times

    key = 'nearby_agents'
    call_counts[key] = call_counts.get(key, 0) + 1

    t_start = time.perf_counter()
    result = original_nearby(self, x, y, radius)
    t_elapsed = (time.perf_counter() - t_start) * 1000

    call_times[key] = call_times.get(key, 0) + t_elapsed

    return result

SpatialHashGrid.nearby_agents = patched_nearby

# Now run simulation
from match_simulation_engine_v2 import Match, create_sample_teams

print("[PROFILER] Counting function calls during 1 frame")
print("=" * 80)

home, away = create_sample_teams()
match = Match(home, away)

all_players = home.players + away.players
for player in all_players:
    match.spatial_grid.add_agent(player, player.x, player.y)

if all_players:
    match.ball_holder = all_players[0]
    match.ball_holder.has_ball = True
    match.ball_possession = "Home"

print("Running 1 frame...")
start = time.perf_counter()

match.current_frame = 0
match.current_minute = 0
match.simulate_frame(dt=1.0/60.0)

end = time.perf_counter()
total_ms = (end - start) * 1000

print()
print("=" * 80)
print(f"FRAME TIME: {total_ms:.2f}ms")
print()
print("FUNCTION CALL ANALYSIS:")
print("-" * 80)

for func, count in sorted(call_counts.items(), key=lambda x: x[1], reverse=True):
    total_time = call_times[func]
    avg_time = total_time / count
    print(f"{func}:")
    print(f"  Called: {count} times")
    print(f"  Total time: {total_time:.2f}ms")
    print(f"  Average: {avg_time:.4f}ms per call")
    print()
