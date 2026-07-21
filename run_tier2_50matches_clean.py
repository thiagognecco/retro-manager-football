#!/usr/bin/env python3
"""
TIER 2 Integration Test - 50 Matches (CLEAN RUN)
Force fresh imports by clearing pycache
"""

import sys
import os
import shutil

# Clear pycache
pycache_dir = r"C:\Users\gnecc\Documents\Footbal manager\__pycache__"
if os.path.exists(pycache_dir):
    shutil.rmtree(pycache_dir)
    print("Cleared __pycache__")

sys.path.insert(0, r"C:\Users\gnecc\Documents\Footbal manager")

import time
import statistics
from contextlib import redirect_stdout, redirect_stderr

# Fresh imports
from match_simulation_engine_v2 import Match, create_sample_teams
from match_simulation_engine_v2_extended import integrate_extended_systems

output_file = r"C:\Users\gnecc\Documents\Footbal manager\TIER2_TEST_RESULTS_CLEAN.txt"

with open(output_file, 'w') as f:
    f.write("=" * 140 + "\n")
    f.write("TIER 2 INTEGRATION TEST - 50 Matches (CLEAN RUN)\n")
    f.write("=" * 140 + "\n\n")

    num_matches = 50
    results = {
        'corners': [],
        'corners_scored': [],
        'free_kicks': [],
        'free_kicks_scored': [],
        'set_piece_goals': [],
        'avg_form': [],
        'hot_streaks': [],
        'cold_streaks': [],
        'goals': [],
        'times': [],
        'fouls': [],
        'yellows': [],
        'injuries': [],
    }

    dev_null = open(os.devnull, 'w')

    f.write(f"Running {num_matches} matches with TIER 1 + TIER 2 systems (CLEAN)...\n\n")
    f.flush()

    start_total = time.perf_counter()

    for match_num in range(1, num_matches + 1):
        match_start = time.perf_counter()

        try:
            with redirect_stdout(dev_null), redirect_stderr(dev_null):
                home, away = create_sample_teams()
                match = Match(home, away)
                integrate_extended_systems(match)

                for minute in range(90):
                    match.current_minute = minute
                    match.current_frame = minute * 60  # Ensure current_frame is set
                    with redirect_stdout(dev_null), redirect_stderr(dev_null):
                        match.simulate_minute()
                    match.process_extended_events()

                match.apply_end_of_match_form_decay()

            match_time = time.perf_counter() - match_start

            extended_stats = match.get_extended_stats()
            h_score = match.home_team.score
            a_score = match.away_team.score

            set_pieces = extended_stats.get('set_pieces', {})
            player_form = extended_stats.get('player_form', {})

            results['corners'].append(set_pieces.get('corners_total', 0))
            results['corners_scored'].append(set_pieces.get('corners_scored', 0))
            results['free_kicks'].append(set_pieces.get('free_kicks_total', 0))
            results['free_kicks_scored'].append(set_pieces.get('free_kicks_scored', 0))
            results['set_piece_goals'].append(set_pieces.get('set_piece_goals', 0))
            results['avg_form'].append(player_form.get('avg_form', 0.0))
            results['hot_streaks'].append(player_form.get('hot_streak_count', 0))
            results['cold_streaks'].append(player_form.get('cold_streak_count', 0))
            results['goals'].append(h_score + a_score)
            results['fouls'].append(extended_stats.get('total_fouls', 0))
            results['yellows'].append(extended_stats.get('total_yellows', 0))
            results['injuries'].append(extended_stats.get('total_injuries', 0))
            results['times'].append(match_time)

            status = f"Match {match_num:2d}: {h_score}-{a_score} | Corners:{set_pieces.get('corners_total', 0):2d} ({set_pieces.get('corners_scored', 0)}) | FKs:{set_pieces.get('free_kicks_total', 0)} ({set_pieces.get('free_kicks_scored', 0)}) | Form:{player_form.get('avg_form', 0.0):+.2f} | {match_time:.1f}s\n"
            f.write(status)
            f.flush()

            elapsed = time.perf_counter() - start_total
            eta = (elapsed / match_num) * (num_matches - match_num)
            print(f"Match {match_num:2d}/{num_matches}: {match_time:.1f}s (ETA: {eta/60:.1f}min)")

        except Exception as e:
            f.write(f"ERROR in Match {match_num}: {str(e)}\n")
            f.flush()
            print(f"ERROR in Match {match_num}: {str(e)}")

    dev_null.close()
    end_total = time.perf_counter()
    total_time = end_total - start_total

    f.write("\n" + "=" * 140 + "\n")
    f.write("ANALYSIS RESULTS\n")
    f.write("=" * 140 + "\n\n")

    avg_corners = statistics.mean(results['corners']) if results['corners'] else 0
    avg_corners_scored = statistics.mean(results['corners_scored']) if results['corners_scored'] else 0
    avg_free_kicks = statistics.mean(results['free_kicks']) if results['free_kicks'] else 0
    avg_free_kicks_scored = statistics.mean(results['free_kicks_scored']) if results['free_kicks_scored'] else 0
    avg_set_piece_goals = statistics.mean(results['set_piece_goals']) if results['set_piece_goals'] else 0
    avg_form = statistics.mean(results['avg_form']) if results['avg_form'] else 0
    avg_hot = statistics.mean(results['hot_streaks']) if results['hot_streaks'] else 0
    avg_cold = statistics.mean(results['cold_streaks']) if results['cold_streaks'] else 0
    avg_goals = statistics.mean(results['goals']) if results['goals'] else 0
    avg_fouls = statistics.mean(results['fouls']) if results['fouls'] else 0
    avg_yellows = statistics.mean(results['yellows']) if results['yellows'] else 0
    avg_injuries = statistics.mean(results['injuries']) if results['injuries'] else 0

    f.write("SET PIECES:\n")
    f.write(f"  Corners/match: {avg_corners:5.1f} (target: 10-12)\n")
    f.write(f"  Corners scored: {avg_corners_scored:5.1f} per match\n")
    f.write(f"  Free kicks/match: {avg_free_kicks:5.1f} (target: 3-4)\n")
    f.write(f"  Free kicks scored: {avg_free_kicks_scored:5.1f} per match\n")
    f.write(f"  Set piece goals: {avg_set_piece_goals:5.1f} per match (~25% of total)\n")
    f.write(f"  Set piece %% of all goals: {(avg_set_piece_goals/avg_goals*100) if avg_goals > 0 else 0:.1f}%%\n\n")

    f.write("PLAYER FORM:\n")
    f.write(f"  Avg form: {avg_form:+5.2f} (-10 to +10 scale)\n")
    f.write(f"  Hot streaks: {avg_hot:5.1f} players per match\n")
    f.write(f"  Cold streaks: {avg_cold:5.1f} players per match\n\n")

    f.write("TIER 1 (Reference):\n")
    f.write(f"  Fouls/match: {avg_fouls:5.1f} (target: 20.9)\n")
    f.write(f"  Yellow cards: {avg_yellows:5.1f} (target: 2-3)\n")
    f.write(f"  Injuries: {avg_injuries:5.1f} (target: 1-2)\n\n")

    f.write("PERFORMANCE:\n")
    f.write(f"  Total matches: {num_matches}\n")
    f.write(f"  Total time: {total_time:.1f}s\n")
    f.write(f"  Avg time/match: {total_time/num_matches:.1f}s\n")
    f.write(f"  Avg goals/match: {avg_goals:.2f}\n\n")

    f.write("=" * 140 + "\n")
    f.write("TEST COMPLETE\n")
    f.write("=" * 140 + "\n")

print(f"\nTest complete! Results saved to:\n{output_file}")
print(f"Total time: {total_time/60:.1f} minutes")
