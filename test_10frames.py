#!/usr/bin/env python3
"""Test 10 frames to see immediate timing breakdown"""

import time
from match_simulation_engine_v2 import Match, create_sample_teams

print("[TEST] Starting 10-frame simulation with timing prints...")
print("=" * 80)

home, away = create_sample_teams()
match = Match(home, away)

start = time.perf_counter()

for frame in range(10):
    match.current_frame = frame
    match.current_minute = 0
    match.simulate_frame(dt=1.0/60.0)
    elapsed = (time.perf_counter() - start) * 1000
    print(f"Frame {frame}: +{elapsed:.2f}ms total")

end = time.perf_counter()
total_ms = (end - start) * 1000
avg_per_frame = total_ms / 10

print("\n" + "=" * 80)
print(f"TOTAL TIME FOR 10 FRAMES: {total_ms:.2f}ms")
print(f"Average per frame: {avg_per_frame:.2f}ms")
print("=" * 80)

if avg_per_frame < 10:
    print(f"[GOOD] Average {avg_per_frame:.2f}ms/frame (target: <2ms, tolerance: <10ms)")
elif avg_per_frame < 20:
    print(f"[SLOW] Average {avg_per_frame:.2f}ms/frame (need optimization)")
else:
    print(f"[VERY SLOW] Average {avg_per_frame:.2f}ms/frame (critical bottleneck)")
