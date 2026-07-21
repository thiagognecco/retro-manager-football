#!/usr/bin/env python3
"""
5-Match Benchmark with Detailed Profiling Analysis
"""

import time
import sys
import re
from io import StringIO
from contextlib import redirect_stdout
from match_simulation_engine_v2 import Match, create_sample_teams
from match_simulation_engine_v2_extended import integrate_extended_systems

# Capture frame output
captured_frames = []

class FrameCapture:
    def __init__(self):
        self.data = []

    def __call__(self, line):
        if '[FRAME' in line or 'Total:' in line or 'ms' in line:
            self.data.append(line)

# Track timing data
frame_times = {
    'tactical_state': [],
    'graph_build': [],
    'predict_pos': [],
    'behaviors': [],
    'grid_rebuild': [],
    'events': []
}

print("="*80)
print("TIER 1+2 BENCHMARK - 5 MATCHES WITH PROFILING")
print("="*80)

start_total = time.perf_counter()

for match_num in range(1, 6):
    match_start = time.perf_counter()

    home, away = create_sample_teams()
    match = Match(home, away)
    integrate_extended_systems(match)

    for minute in range(90):
        match.current_minute = minute
        match.simulate_minute()
        match.process_extended_events()

    match.apply_end_of_match_form_decay()

    match_time = time.perf_counter() - match_start
    print(f"Match {match_num}: {match_time:.1f}s")

total = time.perf_counter() - start_total

print("\n" + "="*80)
print("RESULTS")
print("="*80)
print(f"Total time: {total:.1f}s")
print(f"Avg time/match: {total/5:.1f}s")
print(f"Frames processed: {5*5400}")
print(f"FPS: {5*5400/(total):.0f} frames/second")
print("="*80)
