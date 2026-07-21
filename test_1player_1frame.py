#!/usr/bin/env python3
"""Test 1 player 1 frame to isolate behavior tree"""

import time
from player_behavior import Player, PlayerRole, PlayerState, build_match_context
from spatial_hash_grid import SpatialHashGrid

print("[TEST] Testing 1 PLAYER 1 FRAME with behavior tree")
print("=" * 80)

# Create spatial grid with just 1 player
grid = SpatialHashGrid(cell_size=5, width=100, height=70)

# Create 1 player
player = Player(
    id=1,
    name="Test Player",
    team="Home",
    role=PlayerRole.MIDFIELDER,
    number=5,
    x=50.0,
    y=35.0,
)

# Add to grid
grid.add_agent(player, player.x, player.y)

print(f"Setup:")
print(f"  - 1 player in grid")
print(f"  - Behavior tree initialized")
print()

# Build context
context = build_match_context({
    'spatial_grid': grid,
    'ball_holder': None,
    'ball_position': (50.0, 35.0),
})

print("Running behavior tree tick...")
print("=" * 80)

start = time.perf_counter()

# Tick behavior tree 1 time
result = player.update_behavior(context)

end = time.perf_counter()
elapsed_ms = (end - start) * 1000

print()
print("=" * 80)
print(f"1 PLAYER BEHAVIOR TICK: {elapsed_ms:.2f}ms")
print(f"Player action: {result}")
print("=" * 80)

if elapsed_ms < 10:
    print(f"[GOOD] {elapsed_ms:.2f}ms per player")
else:
    print(f"[SLOW] {elapsed_ms:.2f}ms per player - 1 player alone is slow!")
    print(f"If each of 22 players takes this long: {elapsed_ms * 22:.0f}ms total!")
