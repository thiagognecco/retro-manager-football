#!/usr/bin/env python3
"""
TIER 2 Integration Test - Set Pieces + Player Form
Runs 50 matches with all systems (TIER 1 + TIER 2) enabled
Compares with Football Manager + Premier League real data
"""

import sys
sys.path.insert(0, r"C:\Users\gnecc\Documents\Footbal manager")

import time
import statistics
import os
from contextlib import redirect_stdout, redirect_stderr
from match_simulation_engine_v2 import Match, create_sample_teams
from match_simulation_engine_v2_extended import integrate_extended_systems

print("=" * 140)
print("TIER 2 INTEGRATION TEST - Set Pieces + Player Form Systems".center(140))
print("=" * 140)
print()

# Test configuration
num_matches = 50
results = {
    # TIER 1 stats
    'fouls': [],
    'yellows': [],
    'reds': [],
    'injuries': [],
    'substitutions': {'home': [], 'away': []},
    'goals': [],

    # TIER 2 Set Pieces stats
    'corners': [],
    'corners_scored': [],
    'free_kicks': [],
    'free_kicks_scored': [],
    'set_piece_goals': [],
    'set_piece_xg': [],

    # TIER 2 Form stats
    'avg_form': [],
    'hot_streaks': [],
    'cold_streaks': [],

    'times': [],
}

dev_null = open(os.devnull, 'w')

print(f"Running {num_matches} matches with TIER 1 + TIER 2 systems...\n")

start_total = time.perf_counter()

for match_num in range(1, num_matches + 1):
    match_start = time.perf_counter()

    with redirect_stdout(dev_null), redirect_stderr(dev_null):
        home, away = create_sample_teams()
        match = Match(home, away)

        # Integrate extended systems (TIER 1 + TIER 2)
        integrate_extended_systems(match)

        # Run match
        for minute in range(90):
            match.current_minute = minute

            with redirect_stdout(dev_null), redirect_stderr(dev_null):
                match.simulate_minute()

            # Process extended systems each minute
            match.process_extended_events()

        # Apply form decay at end of match
        match.apply_end_of_match_form_decay()

    match_time = time.perf_counter() - match_start

    # Collect data
    extended_stats = match.get_extended_stats()

    h_score = match.home_team.score
    a_score = match.away_team.score

    # TIER 1 data
    results['fouls'].append(extended_stats.get('total_fouls', 0))
    results['yellows'].append(extended_stats.get('total_yellows', 0))
    results['reds'].append(extended_stats.get('total_reds', 0))
    results['injuries'].append(extended_stats.get('total_injuries', 0))
    results['substitutions']['home'].append(extended_stats['substitutions'].get('home', 0))
    results['substitutions']['away'].append(extended_stats['substitutions'].get('away', 0))
    results['goals'].append(h_score + a_score)

    # TIER 2 Set Pieces data
    set_pieces = extended_stats.get('set_pieces', {})
    results['corners'].append(set_pieces.get('corners_total', 0))
    results['corners_scored'].append(set_pieces.get('corners_scored', 0))
    results['free_kicks'].append(set_pieces.get('free_kicks_total', 0))
    results['free_kicks_scored'].append(set_pieces.get('free_kicks_scored', 0))
    results['set_piece_goals'].append(set_pieces.get('set_piece_goals', 0))
    results['set_piece_xg'].append(set_pieces.get('set_piece_xg', 0.0))

    # TIER 2 Form data
    player_form = extended_stats.get('player_form', {})
    results['avg_form'].append(player_form.get('avg_form', 0.0))
    results['hot_streaks'].append(player_form.get('hot_streak_count', 0))
    results['cold_streaks'].append(player_form.get('cold_streak_count', 0))

    results['times'].append(match_time)

    # Print progress
    print(f"Match {match_num:2d}: {h_score}-{a_score} | "
          f"Corners: {set_pieces.get('corners_total', 0)} ({set_pieces.get('corners_scored', 0)} goals) | "
          f"FKs: {set_pieces.get('free_kicks_total', 0)} ({set_pieces.get('free_kicks_scored', 0)} goals) | "
          f"Form: {player_form.get('avg_form', 0.0):+.2f} | "
          f"Hot: {player_form.get('hot_streak_count', 0)} Cold: {player_form.get('cold_streak_count', 0)} | "
          f"Time: {match_time:.2f}s")

dev_null.close()
end_total = time.perf_counter()
total_time = end_total - start_total

print()
print("=" * 140)
print("TIER 2 SYSTEMS VALIDATION".center(140))
print("=" * 140)
print()

# ============================================================================
# TIER 1 ANALYSIS (for reference)
# ============================================================================

print("TIER 1 ANALYSIS (Card, Injury, Substitution Systems):".upper())
print("-" * 140)

avg_fouls = statistics.mean(results['fouls'])
avg_yellows = statistics.mean(results['yellows'])
avg_reds = statistics.mean(results['reds'])
avg_injuries = statistics.mean(results['injuries'])

print(f"  Fouls per match:      {avg_fouls:6.1f}  (FM target: 20.9)     {'✓ MATCH' if 18 < avg_fouls < 24 else '✗ TUNE'}")
print(f"  Yellow cards/match:   {avg_yellows:6.1f}  (FM target: 2-3)       {'✓ MATCH' if 1.5 < avg_yellows < 3.5 else '✗ TUNE'}")
print(f"  Red cards/match:      {avg_reds:6.1f}  (FM target: 0.1-0.2)  {'✓ OK' if 0 < avg_reds < 0.5 else '✗ TUNE'}")
print(f"  Injuries/match:       {avg_injuries:6.1f}  (FM target: 1-2)       {'✓ MATCH' if 0.8 < avg_injuries < 2.5 else '✗ TUNE'}")
print()

# ============================================================================
# TIER 2 - SET PIECES ANALYSIS
# ============================================================================

print("TIER 2 SET PIECES ANALYSIS (vs Premier League 2025-26):".upper())
print("-" * 140)

avg_corners = statistics.mean(results['corners'])
avg_corners_scored = statistics.mean(results['corners_scored'])
avg_free_kicks = statistics.mean(results['free_kicks'])
avg_free_kicks_scored = statistics.mean(results['free_kicks_scored'])
avg_set_piece_goals = statistics.mean(results['set_piece_goals'])
avg_set_piece_xg = statistics.mean(results['set_piece_xg'])
avg_goals = statistics.mean(results['goals'])

print(f"\n  CORNERS:")
print(f"    Per match:          {avg_corners:6.1f}  (PL target: 10-12)     {'✓ MATCH' if 9 < avg_corners < 13 else '✗ TUNE'}")
print(f"    Goals/match:        {avg_corners_scored:6.1f}  (Expected: ~0.5)")
print(f"    Conversion rate:    {(avg_corners_scored/avg_corners*100) if avg_corners > 0 else 0:6.1f}%  (PL target: 5.3% inswing, 3.6% outswing)")

print(f"\n  FREE KICKS:")
print(f"    Per match:          {avg_free_kicks:6.1f}  (PL target: 3-4)      {'✓ MATCH' if 2 < avg_free_kicks < 5 else '✗ TUNE'}")
print(f"    Goals/match:        {avg_free_kicks_scored:6.1f}  (Expected: ~0.1)")
print(f"    Conversion rate:    {(avg_free_kicks_scored/avg_free_kicks*100) if avg_free_kicks > 0 else 0:6.1f}%  (PL target: 0.2%)")

print(f"\n  SET PIECES OVERALL:")
print(f"    Total goals:        {avg_set_piece_goals:6.1f}  per match")
print(f"    Total xG:           {avg_set_piece_xg:6.2f}  per match")
print(f"    % of all goals:     {(avg_set_piece_goals/avg_goals*100) if avg_goals > 0 else 0:6.1f}%  (PL target: ~25%)")

print()

# ============================================================================
# TIER 2 - PLAYER FORM ANALYSIS
# ============================================================================

print("TIER 2 PLAYER FORM ANALYSIS (Confidence & Streaks):".upper())
print("-" * 140)

avg_form = statistics.mean(results['avg_form'])
avg_hot = statistics.mean(results['hot_streaks'])
avg_cold = statistics.mean(results['cold_streaks'])

print(f"\n  FORM METRICS:")
print(f"    Average team form:  {avg_form:+6.2f}  (scale: -10 to +10)")
print(f"    Hot streak count:   {avg_hot:6.1f}  players per match (expected: 1-3)")
print(f"    Cold streak count:  {avg_cold:6.1f}  players per match (expected: 1-3)")

# Analyze form distribution
hot_matches = sum(1 for f in results['hot_streaks'] if f > 0)
cold_matches = sum(1 for f in results['cold_streaks'] if f > 0)

print(f"\n  STREAK PATTERNS:")
print(f"    Matches with hot streaks:  {hot_matches}/{num_matches} ({hot_matches/num_matches*100:.1f}%)")
print(f"    Matches with cold streaks: {cold_matches}/{num_matches} ({cold_matches/num_matches*100:.1f}%)")
print(f"    Status: {'✓ HEALTHY DISTRIBUTION' if hot_matches/num_matches > 0.3 and cold_matches/num_matches > 0.3 else '✗ NEEDS TUNING'}")

print()

# ============================================================================
# OVERALL STATISTICS
# ============================================================================

print("OVERALL STATISTICS:".upper())
print("-" * 140)

print(f"\n  PERFORMANCE:")
print(f"    Total matches:      {num_matches}")
print(f"    Total time:         {total_time:.1f}s ({total_time/num_matches:.2f}s per match)")
print(f"    Average goals:      {avg_goals:.2f} per match")

print()
print("=" * 140)

# ============================================================================
# SUMMARY CHECKLIST
# ============================================================================

print("\nVALIDATION CHECKLIST:".upper())
print("-" * 140)

checklist = [
    ("Corners per match (10-12)", 9 < avg_corners < 13),
    ("Free kicks per match (3-4)", 2 < avg_free_kicks < 5),
    ("Set piece goals % of total (~25%)", 15 < (avg_set_piece_goals/avg_goals*100) < 35 if avg_goals > 0 else False),
    ("Hot streaks present", hot_matches/num_matches > 0.3),
    ("Cold streaks present", cold_matches/num_matches > 0.3),
    ("Performance acceptable (<5s/match)", statistics.mean(results['times']) < 5.0),
]

passed = 0
for check, status in checklist:
    symbol = "✓" if status else "✗"
    print(f"  {symbol} {check}")
    if status:
        passed += 1

print(f"\nPassed: {passed}/{len(checklist)} checks")
print()

# ============================================================================
# REALISM SCORING
# ============================================================================

print("REALISM SCORING (70% TIER 1 → 85% TARGET WITH TIER 2):".upper())
print("-" * 140)

scoring = {
    "Movement": 70,
    "Stamina": 70,
    "Behavior": 70,
    "Discipline (TIER 1)": 80,
    "Injuries (TIER 1)": 75,
    "Substitutions (TIER 1)": 60,
    "Set Pieces (TIER 2)": 75 if avg_corners > 9 and avg_free_kicks > 2 else 50,
    "Player Form (TIER 2)": 80 if hot_matches/num_matches > 0.3 else 50,
}

for category, score in scoring.items():
    bar_length = score // 5
    bar = "█" * bar_length + "░" * (20 - bar_length)
    print(f"  {category:30s} │{bar}│ {score:3d}%")

overall = sum(scoring.values()) // len(scoring)
print(f"\n  {'OVERALL REALISM':30s} │{'█' * (overall // 5)}{'░' * (20 - overall // 5)}│ {overall:3d}%")
print(f"  Target was: 85% → {'✓ TARGET ACHIEVED!' if overall >= 85 else '✗ CONTINUE OPTIMIZATION'}")

print()
print("=" * 140)
