#!/usr/bin/env python3
"""Replicate EXACTLY what simulate_frame does"""

import time
from match_simulation_engine_v2 import Match, create_sample_teams
from player_behavior import build_match_context, PlayerState

print("[TEST] Exact simulate_frame loop replication")
print("=" * 80)

home, away = create_sample_teams()
match = Match(home, away)

all_players = home.players + away.players

# Setup grid
for player in all_players:
    match.spatial_grid.add_agent(player, player.x, player.y)

if all_players:
    match.ball_holder = all_players[0]
    match.ball_holder.has_ball = True
    match.ball_possession = "Home"

print(f"Setup: 22 players in grid, match context ready")
print()

# Test: Run EXACTLY the behavior loop from simulate_frame
print("Running behavior loop step-by-step:")
print("=" * 80)

# This is exactly what simulate_frame() does:

start = time.perf_counter()

# Step 1: Tactical state update (t1-t2)
t1 = time.perf_counter()
match.tactical_state.update(
    all_players,
    match.ball_position,
    match.ball_possession,
    {'Home': match.home_team.score, 'Away': match.away_team.score}
)
t2 = time.perf_counter()

print(f"Step 1 - Tactical State: {(t2-t1)*1000:.2f}ms")

# Step 2: Build graph (t2-t3)
match.tactical_graph.build_graph(all_players, match.tactical_state.to_dict())
t3 = time.perf_counter()
print(f"Step 2 - Graph Build: {(t3-t2)*1000:.2f}ms")

# Step 3: Predict positions (t3-t4)
ideal_positions = match.tactical_graph.predict_positions(
    all_players,
    match.tactical_state.to_dict(),
    match.home_team.formation if match.ball_possession == "Home" else match.away_team.formation
)
t4 = time.perf_counter()
print(f"Step 3 - Predict Pos: {(t4-t3)*1000:.2f}ms")

# Step 4: Build context (t4-t4b)
t4b_start = time.perf_counter()
context = build_match_context({
    'spatial_grid': match.spatial_grid,
    'ball_holder': match.ball_holder,
    'ball_position': match.ball_position,
})
t4b = time.perf_counter()
print(f"Step 4 - Build Context: {(t4b-t4b_start)*1000:.2f}ms")

# Step 5: THE BIG LOOP (t4b-t5)
t5_start = time.perf_counter()

for player in all_players:
    # A: Update behavior
    player.update_behavior(context)

    # B: Set target based on state
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

    # C: Update movement
    match.movement_controllers[player.id].update(dt=1.0/60.0)

t5 = time.perf_counter()

print(f"Step 5 - BIG LOOP (22x behaviors + targets + movement): {(t5-t5_start)*1000:.2f}ms")

# Step 6: Rebuild grid (t5-t6)
grid_start = time.perf_counter()
match.spatial_grid.clear()
for player in all_players:
    match.spatial_grid.add_agent(player, player.x, player.y)
t6 = time.perf_counter()
print(f"Step 6 - Grid Rebuild: {(t6-grid_start)*1000:.2f}ms")

# Step 7: Events (t6-t7)
event_start = time.perf_counter()
match._process_events()
t7 = time.perf_counter()
print(f"Step 7 - Events: {(t7-event_start)*1000:.2f}ms")

end = time.perf_counter()
total = (end - start) * 1000

print()
print("=" * 80)
print(f"TOTAL: {total:.2f}ms")
print("=" * 80)

if total < 100:
    print("[GOOD] Manual loop is fast!")
else:
    print(f"[SLOW] Manual loop is {total:.0f}ms - BOTTLENECK FOUND HERE!")
