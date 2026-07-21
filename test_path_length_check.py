#!/usr/bin/env python3
"""Check if path length is different based on order"""

from match_simulation_engine_v2 import Match, create_sample_teams
from player_behavior import build_match_context, PlayerState

print("[TEST] Path Length Check - Behavior First vs Movement First")
print("=" * 80)

# Test 1: Behavior first
print("\nTest 1: BEHAVIOR first, then MOVEMENT")
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

path_lengths_1 = []

for player in all_players1:
    # BEHAVIOR FIRST
    player.update_behavior(context1)

    # THEN movement (just set target, don't update yet)
    # Force into movement state for testing
    player.state = PlayerState.MOVING_TO_POSITION
    target = ideal_positions1.get(player.id, (player.x, player.y))
    match1.movement_controllers[player.id].set_target(target)
    path_len = len(match1.movement_controllers[player.id].path)
    path_lengths_1.append(path_len)

if path_lengths_1:
    print(f"Average path length (behavior first): {sum(path_lengths_1)/len(path_lengths_1):.1f}")
    print(f"Max path length: {max(path_lengths_1)}")
    print(f"Min path length: {min(path_lengths_1)}")
else:
    print("No paths created")

# Test 2: Movement first
print("\nTest 2: MOVEMENT first, then BEHAVIOR")
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

path_lengths_2 = []

for player in all_players2:
    # MOVEMENT FIRST (just set target)
    # Force into movement state
    player.state = PlayerState.MOVING_TO_POSITION
    target = ideal_positions2.get(player.id, (player.x, player.y))
    match2.movement_controllers[player.id].set_target(target)
    path_len = len(match2.movement_controllers[player.id].path)
    path_lengths_2.append(path_len)

    # THEN behavior
    player.update_behavior(context2)

if path_lengths_2:
    print(f"Average path length (movement first): {sum(path_lengths_2)/len(path_lengths_2):.1f}")
    print(f"Max path length: {max(path_lengths_2)}")
    print(f"Min path length: {min(path_lengths_2)}")
else:
    print("No paths created")

print()
print("=" * 80)
if sum(path_lengths_1) != sum(path_lengths_2):
    print(f"[DIFFERENCE FOUND] Path length differs!")
    print(f"  Behavior first: total = {sum(path_lengths_1)}")
    print(f"  Movement first: total = {sum(path_lengths_2)}")
else:
    print("Path lengths are the same")
