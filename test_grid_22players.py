#!/usr/bin/env python3
"""Test spatial grid performance with 22 players"""

import time
from spatial_hash_grid import SpatialHashGrid
from player_behavior import Player, PlayerRole

print("[TEST] Spatial Grid Performance with 22 Players")
print("=" * 80)

# Create grid
grid = SpatialHashGrid(cell_size=5, width=100, height=70)

# Create 22 players (11 per team)
players = []
for i in range(22):
    player = Player(
        id=i,
        name=f"Player {i}",
        team="Home" if i < 11 else "Away",
        role=PlayerRole.MIDFIELDER,
        number=(i % 11) + 1,
        x=float(30 + (i % 10) * 5),
        y=float(25 + (i // 10) * 10),
    )
    players.append(player)
    grid.add_agent(player, player.x, player.y)

print(f"Grid setup:")
print(f"  - 22 players added")
print(f"  - Grid size: 100x70m")
print(f"  - Cell size: 5m")
print()

# Test 1: Query from each player
print("Test 1: Each player queries nearby agents")
print("-" * 80)

start = time.perf_counter()

for player in players:
    # Each player queries nearby (like in behavior tree)
    nearby = grid.nearby_agents(player.x, player.y, radius=15)

query_time = (time.perf_counter() - start) * 1000

print(f"22 players × nearby_agents(radius=15): {query_time:.2f}ms")
print(f"Average per player: {query_time/22:.2f}ms")
print()

# Test 2: Full tick simulation
print("Test 2: Simulating full update (all players update + grid rebuild)")
print("-" * 80)

start = time.perf_counter()

# Clear and rebuild grid (like in simulate_frame)
grid.clear()
for player in players:
    grid.add_agent(player, player.x, player.y)

rebuild_time = (time.perf_counter() - start) * 1000

# Each player queries
query_start = time.perf_counter()
for player in players:
    nearby = grid.nearby_agents(player.x, player.y, radius=15)
    nearby_filtered = [a for a in nearby if hasattr(a, 'team') and a.team != player.team]

query_time2 = (time.perf_counter() - query_start) * 1000

print(f"Grid rebuild: {rebuild_time:.2f}ms")
print(f"22 players query + filter: {query_time2:.2f}ms")
print(f"Total: {rebuild_time + query_time2:.2f}ms")
print()

if (rebuild_time + query_time2) < 100:
    print("[GOOD] Grid performance is acceptable")
else:
    print(f"[SLOW] Grid operations taking {rebuild_time + query_time2:.0f}ms")
