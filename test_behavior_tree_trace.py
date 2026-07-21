#!/usr/bin/env python3
"""Instrument behavior tree to count function calls"""

import time
from player_behavior import Player, PlayerRole, PlayerState, build_match_context
from spatial_hash_grid import SpatialHashGrid

# Global counters
call_stats = {}

def record_call(func_name):
    """Record a function call"""
    if func_name not in call_stats:
        call_stats[func_name] = {'count': 0, 'time': 0}
    call_stats[func_name]['count'] += 1

# Monkey-patch all Task classes to record calls
from player_behavior import (
    Task_HasBall, Task_CanShoot, Task_CanPass, Task_IsPressed,
    Task_Shoot, Task_Pass, Task_MoveToPosition, Task_Defend, Task_Press,
    Selector, Sequence
)

original_has_ball_tick = Task_HasBall.tick
original_can_shoot_tick = Task_CanShoot.tick
original_can_pass_tick = Task_CanPass.tick
original_is_pressed_tick = Task_IsPressed.tick
original_shoot_tick = Task_Shoot.tick
original_pass_tick = Task_Pass.tick
original_move_tick = Task_MoveToPosition.tick
original_defend_tick = Task_Defend.tick
original_press_tick = Task_Press.tick
original_selector_tick = Selector.tick
original_sequence_tick = Sequence.tick

def wrap_tick(cls_name, original_func):
    def wrapper(self, player, context):
        record_call(cls_name)
        return original_func(self, player, context)
    return wrapper

Task_HasBall.tick = wrap_tick('Task_HasBall', original_has_ball_tick)
Task_CanShoot.tick = wrap_tick('Task_CanShoot', original_can_shoot_tick)
Task_CanPass.tick = wrap_tick('Task_CanPass', original_can_pass_tick)
Task_IsPressed.tick = wrap_tick('Task_IsPressed', original_is_pressed_tick)
Task_Shoot.tick = wrap_tick('Task_Shoot', original_shoot_tick)
Task_Pass.tick = wrap_tick('Task_Pass', original_pass_tick)
Task_MoveToPosition.tick = wrap_tick('Task_MoveToPosition', original_move_tick)
Task_Defend.tick = wrap_tick('Task_Defend', original_defend_tick)
Task_Press.tick = wrap_tick('Task_Press', original_press_tick)

# Now import and run simulation
from match_simulation_engine_v2 import create_sample_teams

print("[TRACER] Behavior Tree Call Analysis for 1 Frame")
print("=" * 80)

home, away = create_sample_teams()

all_players = home.players + away.players

# Setup grid
grid = SpatialHashGrid(cell_size=5, width=100, height=70)
for player in all_players:
    grid.add_agent(player, player.x, player.y)

if all_players:
    ball_holder = all_players[0]
    ball_holder.has_ball = True
else:
    ball_holder = None

# Build context
context = build_match_context({
    'spatial_grid': grid,
    'ball_holder': ball_holder,
    'ball_position': (50.0, 35.0),
})

print(f"Setup: 22 players, 1 grid, 1 context")
print(f"Running behavior update for all 22 players...")
print("=" * 80)

start = time.perf_counter()

for player in all_players:
    player.update_behavior(context)

end = time.perf_counter()
total_ms = (end - start) * 1000

print(f"\nTOTAL TIME: {total_ms:.2f}ms")
print()
print("=" * 80)
print("FUNCTION CALL ANALYSIS")
print("=" * 80)

# Sort by call count
sorted_calls = sorted(call_stats.items(), key=lambda x: x[1]['count'], reverse=True)

for func_name, stats in sorted_calls:
    avg_per_call = (total_ms / stats['count']) if stats['count'] > 0 else 0
    print(f"{func_name:30s}: {stats['count']:6d} calls (avg: {avg_per_call:.4f}ms per call)")

print()
print("=" * 80)
print(f"TOTAL CALLS: {sum(s['count'] for s in call_stats.values())}")
print(f"TOTAL TIME: {total_ms:.2f}ms")
print(f"Average time per call: {total_ms / sum(s['count'] for s in call_stats.values()) if call_stats else 0:.4f}ms")
