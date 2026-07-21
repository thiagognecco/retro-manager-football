#!/usr/bin/env python3
"""Check if context is being rebuilt in the loop"""

import time
from match_simulation_engine_v2 import Match, create_sample_teams
from player_behavior import build_match_context, PlayerState

# Monkey patch to count context builds
original_build = build_match_context
context_build_count = 0

def patched_build(match_state):
    global context_build_count
    context_build_count += 1
    return original_build(match_state)

import player_behavior
player_behavior.build_match_context = patched_build

print("[TEST] Context Building Check in Loop")
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

# Get ideal positions
match.tactical_state.update(all_players, match.ball_position, "Home", {'Home': 0, 'Away': 0})
match.tactical_graph.build_graph(all_players, match.tactical_state.to_dict())
ideal_positions = match.tactical_graph.predict_positions(
    all_players, match.tactical_state.to_dict(), match.home_team.formation
)

print(f"Setup: 22 players")
print()

# Run the EXACT loop
print("Running big loop with monitoring:")
print("=" * 80)

context_build_count = 0  # Reset counter

start = time.perf_counter()

# Build context ONCE like simulate_frame does
context = patched_build({
    'spatial_grid': match.spatial_grid,
    'ball_holder': match.ball_holder,
    'ball_position': match.ball_position,
})

for player in all_players:
    # Update behavior
    player.update_behavior(context)

    # Set target
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
print(f"Context builds: {context_build_count} (should be 1)")
print()

if context_build_count > 1:
    print(f"[PROBLEM FOUND!] Context built {context_build_count} times!")
    print(f"Each build might be expensive, causing {total_ms:.0f}ms")
else:
    print("Context built only once - not the problem")
