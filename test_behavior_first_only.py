#!/usr/bin/env python3
"""Test just behavior first order"""

import time
from match_simulation_engine_v2 import Match, create_sample_teams
from player_behavior import build_match_context, PlayerState

print("[TEST] Behavior First - Movement Timing Breakdown")
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

match.tactical_state.update(all_players, match.ball_position, "Home", {'Home': 0, 'Away': 0})
match.tactical_graph.build_graph(all_players, match.tactical_state.to_dict())
ideal_positions = match.tactical_graph.predict_positions(
    all_players, match.tactical_state.to_dict(), match.home_team.formation
)

context = build_match_context({
    'spatial_grid': match.spatial_grid,
    'ball_holder': match.ball_holder,
    'ball_position': match.ball_position,
})

print("Running loop: BEHAVIOR then MOVEMENT...")
print("=" * 80)

start = time.perf_counter()

for player in all_players:
    # BEHAVIOR FIRST
    player.update_behavior(context)

    # THEN movement
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

    print(f"Player {player.id}: updating movement...")
    match.movement_controllers[player.id].update(dt=1.0/60.0)

end = time.perf_counter()
time_ms = (end - start) * 1000

print()
print("=" * 80)
print(f"Total time: {time_ms:.2f}ms")
print("=" * 80)
