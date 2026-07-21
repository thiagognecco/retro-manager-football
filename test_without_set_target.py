#!/usr/bin/env python3
"""Test movement update WITHOUT calling set_target()"""

import time
from match_simulation_engine_v2 import Match, create_sample_teams
from player_behavior import build_match_context, PlayerState

print("[TEST] Movement Update - WITHOUT set_target()")
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

context = build_match_context({
    'spatial_grid': match.spatial_grid,
    'ball_holder': match.ball_holder,
    'ball_position': match.ball_position,
})

print("Running loop: BEHAVIOR then MOVEMENT (no set_target)...")
print("=" * 80)

start = time.perf_counter()

for player in all_players:
    # BEHAVIOR FIRST
    player.update_behavior(context)

    # DO NOT set_target - skip it entirely!
    # Just run movement update directly

    print(f"Player {player.id}: updating movement...")
    match.movement_controllers[player.id].update(dt=1.0/60.0)

end = time.perf_counter()
time_ms = (end - start) * 1000

print()
print("=" * 80)
print(f"Total time (no set_target): {time_ms:.2f}ms")
print("=" * 80)

if time_ms < 100:
    print(f"[GOOD] Without set_target: {time_ms:.0f}ms")
else:
    print(f"[SLOW] Even without set_target: {time_ms:.0f}ms")
    print("Problem is in movement_controller.update() itself!")
