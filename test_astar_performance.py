#!/usr/bin/env python3
"""Test A* pathfinding performance"""

import time
from player_movement import AStarPathfinder

print("[TEST] A* Pathfinding Performance")
print("=" * 80)

pathfinder = AStarPathfinder(width=100, height=70)

# Test 1: Single path (like one player)
print("\nTest 1: Single A* path calculation")
print("-" * 80)

start = time.perf_counter()

path = pathfinder.find_path(
    start=(10.0, 10.0),
    goal=(90.0, 60.0),
    obstacles=[(50.0, 35.0), (51.0, 35.0)],  # 2 obstacles
    obstacle_radius=2.0
)

single_time = (time.perf_counter() - start) * 1000

print(f"Single A* path: {single_time:.2f}ms")
print(f"Path length: {len(path)} waypoints")

# Test 2: 22 paths (like all players in frame)
print("\nTest 2: 22 A* paths (simulating all players)")
print("-" * 80)

start = time.perf_counter()

for i in range(22):
    path = pathfinder.find_path(
        start=(10.0 + i, 10.0),
        goal=(90.0 - i, 60.0),
        obstacles=[(50.0 + j%3, 35.0 + j%3) for j in range(20)],  # 20 obstacles
        obstacle_radius=2.0
    )

total_time = (time.perf_counter() - start) * 1000
avg_per_path = total_time / 22

print(f"22 paths total: {total_time:.2f}ms")
print(f"Average per path: {avg_per_path:.2f}ms")

print()
print("=" * 80)
if avg_per_path > 100:
    print(f"[SLOW] A* takes {avg_per_path:.0f}ms per path - THIS IS THE BOTTLENECK!")
elif avg_per_path > 10:
    print(f"[MEDIUM] A* takes {avg_per_path:.2f}ms per path")
else:
    print(f"[FAST] A* is OK at {avg_per_path:.2f}ms per path")
