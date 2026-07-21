#!/usr/bin/env python3
"""Test just set_target + movement update in the loop"""

import time
from match_simulation_engine_v2 import Match, create_sample_teams
from player_behavior import PlayerState

print("[TEST] Movement + Targets Loop (without behavior)")
print("=" * 80)

home, away = create_sample_teams()
match = Match(home, away)

all_players = home.players + away.players

# Setup
for player in all_players:
    match.spatial_grid.add_agent(player, player.x, player.y)

# Get ideal positions (like in simulate_frame)
match.tactical_state.update(
    all_players, match.ball_position, "Home",
    {'Home': 0, 'Away': 0}
)
match.tactical_graph.build_graph(all_players, match.tactical_state.to_dict())
ideal_positions = match.tactical_graph.predict_positions(
    all_players,
    match.tactical_state.to_dict(),
    match.home_team.formation
)

print(f"Setup: 22 players, ideal positions computed")
print()

# Test: Just the set_target + movement loop (NO behavior update)
print("Loop: set_target() + movement_controller.update()")
print("=" * 80)

start = time.perf_counter()

for player in all_players:
    # Just the movement part (from simulate_frame)
    if player.state == PlayerState.MOVING_TO_POSITION:
        target = ideal_positions.get(player.id, (player.x, player.y))
        match.movement_controllers[player.id].set_target(target)
    elif player.state == PlayerState.PASSING:
        if player.pass_target:
            target = (player.pass_target.x, player.pass_target.y)
            match.movement_controllers[player.id].set_target(target)
    elif player.state == PlayerState.DEFENDING or player.state == PlayerState.PRESSING:
        if player.mark_target or player.press_target:
            target_player = player.mark_target or player.press_target
            target = (target_player.x, target_player.y)
            match.movement_controllers[player.id].set_target(target)

    # Update movement
    match.movement_controllers[player.id].update(dt=1.0/60.0)

end = time.perf_counter()
total_ms = (end - start) * 1000

print(f"Time: {total_ms:.2f}ms")
print()

if total_ms < 100:
    print("[GOOD] Movement + targets is fast!")
else:
    print(f"[SLOW] Movement + targets is {total_ms:.0f}ms")
    print("This is NOT the culprit!")
    print()
    print("The bottleneck must be in update_behavior() when combined with other state...")
