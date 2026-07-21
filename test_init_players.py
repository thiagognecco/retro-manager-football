#!/usr/bin/env python3
"""Test initializing 22 players with behavior trees"""

import time
from player_behavior import Player, PlayerRole

print("[TEST] Initializing 22 Players with Behavior Trees")
print("=" * 80)

start = time.perf_counter()

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

end = time.perf_counter()
init_time = (end - start) * 1000

print(f"Initialized 22 players with behavior trees: {init_time:.2f}ms")
print(f"Average per player: {init_time/22:.2f}ms")
print()

if init_time < 100:
    print("[GOOD] Initialization is fast")
else:
    print("[SLOW] Initialization is slow!")
