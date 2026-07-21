#!/usr/bin/env python3
"""Test if player movement update is the bottleneck"""

import time
from match_simulation_engine_v2 import create_sample_teams
from spatial_hash_grid import SpatialHashGrid

print("[TEST] Movement Update Performance (22 players)")
print("=" * 80)

home, away = create_sample_teams()

all_players = home.players + away.players

# Create spatial grid and movement controllers like in Match
from player_movement import PlayerMovement
grid = SpatialHashGrid(cell_size=5, width=100, height=70)
movement_controllers = {}
for player in all_players:
    movement_controllers[player.id] = PlayerMovement(player, grid)
    grid.add_agent(player, player.x, player.y)

print(f"Setup: 22 players with movement controllers")
print()

# Test 1: Just update movement (no behaviors)
print("Test 1: movement_controller.update(dt) for each player")
print("-" * 80)

start = time.perf_counter()

for player in all_players:
    movement_controllers[player.id].update(dt=1.0/60.0)

move_time = (time.perf_counter() - start) * 1000

print(f"22 × movement.update(): {move_time:.2f}ms")
print(f"Average per player: {move_time/22:.2f}ms")
print()

# Test 2: set_target + update
print("Test 2: set_target() + update() for each player")
print("-" * 80)

start = time.perf_counter()

for player in all_players:
    movement_controllers[player.id].set_target((player.x + 5, player.y + 5))
    movement_controllers[player.id].update(dt=1.0/60.0)

target_time = (time.perf_counter() - start) * 1000

print(f"22 × (set_target + update): {target_time:.2f}ms")
print(f"Average per player: {target_time/22:.2f}ms")
print()

if move_time < 100:
    print("[GOOD] Movement update is fast")
else:
    print("[SLOW] Movement update is slow!")
