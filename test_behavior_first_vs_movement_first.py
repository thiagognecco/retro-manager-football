#!/usr/bin/env python3
"""Test if order matters: behavior first or movement first"""

import time
from match_simulation_engine_v2 import Match, create_sample_teams
from player_behavior import build_match_context, PlayerState

print("[TEST] Order Dependency: Behavior First vs Movement First")
print("=" * 80)

# Setup 1: Behavior first, then movement
print("\nTest 1: BEHAVIOR then MOVEMENT (like simulate_frame)")
print("-" * 80)

home1, away1 = create_sample_teams()
match1 = Match(home1, away1)

all_players1 = home1.players + away1.players

for player in all_players1:
    match1.spatial_grid.add_agent(player, player.x, player.y)

if all_players1:
    match1.ball_holder = all_players1[0]
    match1.ball_holder.has_ball = True
    match1.ball_possession = "Home"

match1.tactical_state.update(all_players1, match1.ball_position, "Home", {'Home': 0, 'Away': 0})
match1.tactical_graph.build_graph(all_players1, match1.tactical_state.to_dict())
ideal_positions1 = match1.tactical_graph.predict_positions(
    all_players1, match1.tactical_state.to_dict(), match1.home_team.formation
)

context1 = build_match_context({
    'spatial_grid': match1.spatial_grid,
    'ball_holder': match1.ball_holder,
    'ball_position': match1.ball_position,
})

start1 = time.perf_counter()

for player in all_players1:
    # BEHAVIOR FIRST
    player.update_behavior(context1)

    # THEN movement
    if player.state == PlayerState.MOVING_TO_POSITION:
        target = ideal_positions1.get(player.id, (player.x, player.y))
        match1.movement_controllers[player.id].set_target(target)
    elif player.state == PlayerState.PASSING:
        if player.pass_target:
            target = (player.pass_target.x, player.pass_target.y)
            match1.movement_controllers[player.id].set_target(target)
    elif player.state == PlayerState.DEFENDING or player.state == PlayerState.PRESSING:
        if player.mark_target or player.press_target:
            target_player = player.mark_target or player.press_target
            target = (target_player.x, target_player.y)
            match1.movement_controllers[player.id].set_target(target)

    match1.movement_controllers[player.id].update(dt=1.0/60.0)

end1 = time.perf_counter()
time1 = (end1 - start1) * 1000

print(f"Time (Behavior->Movement): {time1:.2f}ms")

# Setup 2: Movement first, then behavior
print("\nTest 2: MOVEMENT then BEHAVIOR (reverse order)")
print("-" * 80)

home2, away2 = create_sample_teams()
match2 = Match(home2, away2)

all_players2 = home2.players + away2.players

for player in all_players2:
    match2.spatial_grid.add_agent(player, player.x, player.y)

if all_players2:
    match2.ball_holder = all_players2[0]
    match2.ball_holder.has_ball = True
    match2.ball_possession = "Home"

match2.tactical_state.update(all_players2, match2.ball_position, "Home", {'Home': 0, 'Away': 0})
match2.tactical_graph.build_graph(all_players2, match2.tactical_state.to_dict())
ideal_positions2 = match2.tactical_graph.predict_positions(
    all_players2, match2.tactical_state.to_dict(), match2.home_team.formation
)

context2 = build_match_context({
    'spatial_grid': match2.spatial_grid,
    'ball_holder': match2.ball_holder,
    'ball_position': match2.ball_position,
})

start2 = time.perf_counter()

for player in all_players2:
    # MOVEMENT FIRST
    if player.state == PlayerState.MOVING_TO_POSITION:
        target = ideal_positions2.get(player.id, (player.x, player.y))
        match2.movement_controllers[player.id].set_target(target)
    elif player.state == PlayerState.PASSING:
        if player.pass_target:
            target = (player.pass_target.x, player.pass_target.y)
            match2.movement_controllers[player.id].set_target(target)
    elif player.state == PlayerState.DEFENDING or player.state == PlayerState.PRESSING:
        if player.mark_target or player.press_target:
            target_player = player.mark_target or player.press_target
            target = (target_player.x, target_player.y)
            match2.movement_controllers[player.id].set_target(target)

    match2.movement_controllers[player.id].update(dt=1.0/60.0)

    # THEN behavior
    player.update_behavior(context2)

end2 = time.perf_counter()
time2 = (end2 - start2) * 1000

print(f"Time (Movement->Behavior): {time2:.2f}ms")

print()
print("=" * 80)
print(f"Difference: {abs(time1 - time2):.2f}ms")

if abs(time1 - time2) > 100:
    print(f"[IMPORTANT] Order matters! {abs(time1 - time2):.0f}ms difference")
    if time1 > time2:
        print("Behavior→Movement is slower (affects behavior execution)")
    else:
        print("Movement→Behavior is slower (affects movement execution)")
else:
    print("Order doesn't matter - same performance")
