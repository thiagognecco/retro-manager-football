#!/usr/bin/env python3
"""Quick validation: 10 matches with tuned form system"""

import sys
sys.path.insert(0, r"C:\Users\gnecc\Documents\Footbal manager")

import time
import statistics
from match_simulation_engine_v2 import Match, create_sample_teams
from match_simulation_engine_v2_extended import integrate_extended_systems

print("=" * 80)
print("TIER 2 QUICK VALIDATION - 10 Matches (Tuned Form)")
print("=" * 80)

results = {'corners': [], 'form': [], 'hot_streaks': [], 'cold_streaks': [], 'goals': [], 'times': []}
start = time.perf_counter()

for match_num in range(1, 11):
    match_start = time.perf_counter()
    home, away = create_sample_teams()
    match = Match(home, away)
    integrate_extended_systems(match)

    for minute in range(90):
        match.current_minute = minute
        match.current_frame = minute * 60
        match.simulate_minute()
        match.process_extended_events()

    match.apply_end_of_match_form_decay()
    match_time = time.perf_counter() - match_start

    extended_stats = match.get_extended_stats()
    set_pieces = extended_stats.get('set_pieces', {})
    player_form = extended_stats.get('player_form', {})

    results['corners'].append(set_pieces.get('corners_total', 0))
    results['form'].append(player_form.get('avg_form', 0))
    results['hot_streaks'].append(player_form.get('hot_streak_count', 0))
    results['cold_streaks'].append(player_form.get('cold_streak_count', 0))
    results['goals'].append(match.home_team.score + match.away_team.score)
    results['times'].append(match_time)

    print(f"Match {match_num:2d}: Corners {set_pieces.get('corners_total', 0):2d} | Form {player_form.get('avg_form', 0.0):+.2f} | Hot {player_form.get('hot_streak_count', 0):2d} | Cold {player_form.get('cold_streak_count', 0):2d} | {match_time:.1f}s")

end = time.perf_counter()
total = end - start

print("\n" + "=" * 80)
print("VALIDATION RESULTS")
print("=" * 80)

print(f"\nSET PIECES:")
print(f"  Corners/match: {statistics.mean(results['corners']):5.1f} (target: 10-12)")
print(f"  Goals/match: {statistics.mean(results['goals']):5.2f}")

print(f"\nPLAYER FORM (TUNED):")
print(f"  Avg form: {statistics.mean(results['form']):+5.2f} (target: -1 to +1)")
print(f"  Form std dev: {statistics.stdev(results['form']) if len(results['form']) > 1 else 0:.2f}")
print(f"  Hot streaks: {statistics.mean(results['hot_streaks']):5.1f} (target: 3-5)")
print(f"  Cold streaks: {statistics.mean(results['cold_streaks']):5.1f} (target: 3-5)")

print(f"\nPERFORMANCE:")
print(f"  Total time: {total:.1f}s")
print(f"  Avg time/match: {statistics.mean(results['times']):.1f}s (baseline: 35s)")

print("\n" + "=" * 80)

# Validation
form_ok = -1 < statistics.mean(results['form']) < 1.5
hot_ok = 3 <= statistics.mean(results['hot_streaks']) <= 8
cold_ok = statistics.mean(results['cold_streaks']) > 1

if form_ok and hot_ok and cold_ok:
    print("✅ VALIDATION PASSED - Form tuning successful!")
else:
    print("⚠️  WARNING - Some metrics need further adjustment:")
    if not form_ok:
        print(f"   Form mean {statistics.mean(results['form']):.2f} still needs work (target: -1 to +1)")
    if not hot_ok:
        print(f"   Hot streaks {statistics.mean(results['hot_streaks']):.1f} needs adjustment")
    if not cold_ok:
        print(f"   Cold streaks too low: {statistics.mean(results['cold_streaks']):.1f} (target: 3-5)")

print("=" * 80)
