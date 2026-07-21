#!/usr/bin/env python3
"""Test if context building is the bottleneck"""

import time
from match_simulation_engine_v2 import Match, create_sample_teams
from player_behavior import build_match_context

print("[TEST] Context Building Performance")
print("=" * 80)

home, away = create_sample_teams()
match = Match(home, away)

all_players = home.players + away.players
for player in all_players:
    match.spatial_grid.add_agent(player, player.x, player.y)

print("Testing build_match_context()...")
print("=" * 80)

# Time just the context build
start = time.perf_counter()

for _ in range(1000):  # Call it 1000 times
    context = build_match_context({
        'spatial_grid': match.spatial_grid,
        'ball_holder': all_players[0],
        'ball_position': match.ball_position,
    })

end = time.perf_counter()
total_ms = (end - start) * 1000

print(f"1000 × build_match_context(): {total_ms:.2f}ms")
print(f"Average per call: {total_ms/1000:.4f}ms")
print()

if total_ms < 10:
    print("[GOOD] Context building is fast")
else:
    print("[SLOW] Context building is slow")
