#!/usr/bin/env python3
"""
TIER 2 Form System Tuning Validation - 10 Matches
Test new form parameters to ensure proper balance
"""

import sys
import os
import shutil
import time
from contextlib import redirect_stdout, redirect_stderr

pycache_dir = r"C:\Users\gnecc\Documents\Footbal manager\__pycache__"
if os.path.exists(pycache_dir):
    shutil.rmtree(pycache_dir)

sys.path.insert(0, r"C:\Users\gnecc\Documents\Footbal manager")

from match_simulation_engine_v2 import Match, create_sample_teams
from match_simulation_engine_v2_extended import integrate_extended_systems

def run_tuning_test():
    """Run 10-match tuning test"""
    print("=" * 80)
    print("TIER 2 FORM SYSTEM TUNING VALIDATION - 10 Matches")
    print("=" * 80)
    print()

    total_time = 0
    form_values = []
    hot_streak_matches = 0
    cold_streak_matches = 0

    dev_null = open(os.devnull, 'w')

    for match_num in range(1, 11):
        match_start = time.perf_counter()

        try:
            with redirect_stdout(dev_null), redirect_stderr(dev_null):
                home, away = create_sample_teams()
                match = Match(home, away)
                integrate_extended_systems(match)

                for minute in range(90):
                    match.current_minute = minute
                    match.current_frame = minute * 60
                    with redirect_stdout(dev_null), redirect_stderr(dev_null):
                        match.simulate_minute()
                    match.process_extended_events()

                match.apply_end_of_match_form_decay()

        except Exception as e:
            print(f"Match {match_num} error: {e}")
            continue

        elapsed = time.perf_counter() - match_start
        total_time += elapsed

        form_stats = match.form_system.get_system_stats()
        avg_form = form_stats['avg_form']
        hot_count = form_stats['hot_streak_count']
        cold_count = form_stats['cold_streak_count']

        form_values.append(avg_form)
        hot_streak_matches += hot_count
        cold_streak_matches += cold_count

        h_score = match.home_team.score
        a_score = match.away_team.score
        print(f"Match {match_num:2d}: {h_score}-{a_score} | "
              f"Form:{avg_form:+6.2f} | Hot:{hot_count:2d} | Cold:{cold_count:2d} | {elapsed:6.2f}s")

    print()
    print("=" * 80)
    print("ANALYSIS RESULTS")
    print("=" * 80)
    print()

    avg_form = sum(form_values) / len(form_values) if form_values else 0
    avg_hot = hot_streak_matches / 10
    avg_cold = cold_streak_matches / 10
    avg_time = total_time / 10

    print(f"FORM METRICS:")
    print(f"  Avg form:        {avg_form:+6.2f} (target: -1 to +1)")
    print(f"  Hot streaks:     {avg_hot:6.1f}/match (target: 3-5)")
    print(f"  Cold streaks:    {avg_cold:6.1f}/match (target: 3-5)")
    print()

    print(f"PERFORMANCE:")
    print(f"  Avg time/match:  {avg_time:6.2f}s (target: ~31.4s)")
    print(f"  Total time:      {total_time:6.2f}s")
    print()

    # Validation
    print("VALIDATION:")
    form_ok = -2 <= avg_form <= 2
    hot_ok = 2 <= avg_hot <= 6
    cold_ok = 2 <= avg_cold <= 6
    perf_ok = 30 <= avg_time <= 35

    print(f"  Form in range (-2 to +2):     {'PASS' if form_ok else 'FAIL'}")
    print(f"  Hot streaks reasonable:       {'PASS' if hot_ok else 'FAIL'}")
    print(f"  Cold streaks reasonable:      {'PASS' if cold_ok else 'FAIL'}")
    print(f"  Performance acceptable:       {'PASS' if perf_ok else 'FAIL'}")
    print()

    if form_ok and hot_ok and cold_ok and perf_ok:
        print("ALL CHECKS PASSED - Parameters look good!")
        print("Ready for 100+ match comprehensive test")
        return True
    elif not form_ok:
        print("FORM STILL UNBALANCED")
        if avg_form > 2:
            print("   Form too high, reduce positive values MORE")
        else:
            print("   Form too low, increase positive values")
        return False
    else:
        print("Some metrics need adjustment")
        return False

if __name__ == "__main__":
    try:
        success = run_tuning_test()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
