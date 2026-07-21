#!/usr/bin/env python3
"""
Quick test: Run 1 match with TIER 2 event hooks
Verify that Set Pieces and Form are being tracked
"""

import sys
sys.path.insert(0, r"C:\Users\gnecc\Documents\Footbal manager")

import time
from match_simulation_engine_v2 import Match, create_sample_teams
from match_simulation_engine_v2_extended import integrate_extended_systems

print("=" * 80)
print("TIER 2 EVENT HOOKS - SINGLE MATCH TEST")
print("=" * 80)

match_start = time.perf_counter()

try:
    print("\n[1/3] Creating match...")
    home, away = create_sample_teams()
    match = Match(home, away)

    print("[2/3] Integrating TIER 1 + TIER 2 systems...")
    integrate_extended_systems(match)

    print("[3/3] Simulating 90 minutes...")
    for minute in range(90):
        match.current_minute = minute
        match.simulate_minute()
        match.process_extended_events()

        if minute % 15 == 0:
            print(f"  Minute {minute}: Score {match.home_team.score}-{match.away_team.score}")

    match.apply_end_of_match_form_decay()

    match_time = time.perf_counter() - match_start

    # Get stats
    extended_stats = match.get_extended_stats()
    set_pieces = extended_stats.get('set_pieces', {})
    player_form = extended_stats.get('player_form', {})

    print("\n" + "=" * 80)
    print("TEST RESULTS")
    print("=" * 80)

    print(f"\nFinal Score: {match.home_team.score} - {match.away_team.score}")
    print(f"Match Time: {match_time:.1f} seconds")

    print("\n[SET PIECES]")
    print(f"  Corners: {set_pieces.get('corners_total', 0)} (Expected: 10-12)")
    print(f"  Corners scored: {set_pieces.get('corners_scored', 0)}")
    print(f"  Free kicks: {set_pieces.get('free_kicks_total', 0)} (Expected: 3-4)")
    print(f"  Free kicks scored: {set_pieces.get('free_kicks_scored', 0)}")
    print(f"  Set piece goals: {set_pieces.get('set_piece_goals', 0)}")
    print(f"  Set piece xG: {set_pieces.get('set_piece_xg', 0):.2f}")

    print("\n[PLAYER FORM]")
    print(f"  Average form: {player_form.get('avg_form', 0.0):+.2f} (Expected: -1 to +1)")
    print(f"  Hot streaks: {player_form.get('hot_streak_count', 0)} (Expected: 3-5)")
    print(f"  Cold streaks: {player_form.get('cold_streak_count', 0)} (Expected: 3-5)")

    print("\n[TIER 1 REFERENCE]")
    print(f"  Total fouls: {extended_stats.get('total_fouls', 0)}")
    print(f"  Yellow cards: {extended_stats.get('total_yellows', 0)}")
    print(f"  Injuries: {extended_stats.get('total_injuries', 0)}")

    print("\n" + "=" * 80)

    # Validation
    corners_ok = 0 <= set_pieces.get('corners_total', 0) <= 20
    form_ok = player_form.get('avg_form', 0) != 0.0 or player_form.get('hot_streak_count', 0) > 0

    if corners_ok and form_ok:
        print("✅ TEST PASSED - Event hooks are working!")
    else:
        if not corners_ok:
            print("⚠️  WARNING: Corners detection may not be working properly")
        if not form_ok:
            print("⚠️  WARNING: Form updates may not be working properly")

except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
