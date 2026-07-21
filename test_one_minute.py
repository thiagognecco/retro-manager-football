#!/usr/bin/env python3
"""Test 1 minute simulation to see timing breakdown"""

import time
from match_simulation_engine_v2 import Match, create_sample_teams

print("[TEST] Starting 1-minute simulation with timing prints...")
print("=" * 80)

start = time.perf_counter()

home, away = create_sample_teams()
match = Match(home, away)

# Simulate only 1 minute (60 frames)
for minute in range(1):
    match.current_minute = minute
    match.simulate_minute()
    print(f"\n✓ Minute {minute} completed")

end = time.perf_counter()
total = end - start

print("\n" + "=" * 80)
print(f"TOTAL TIME FOR 1 MINUTE: {total:.2f}s ({total*1000:.0f}ms)")
print(f"Average frame time: {total/60*1000:.2f}ms")
print("=" * 80)

if total < 10:
    print("✓ SUCCESS - 1 minute < 10s")
else:
    print(f"✗ SLOW - 1 minute = {total:.2f}s (target: <10s)")
