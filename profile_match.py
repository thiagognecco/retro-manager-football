import cProfile
import pstats
import io
from match_simulation_engine_v2 import Match, create_sample_teams

def profile_one_match():
    """Profile 1 complete match"""
    home, away = create_sample_teams()
    match = Match(home, away)
    match.simulate_match()

# Profile com saída
pr = cProfile.Profile()
pr.enable()
profile_one_match()
pr.disable()

# Mostrar resultados ordenados por tempo cumulativo
s = io.StringIO()
ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
ps.print_stats(30)  # Top 30 functions
print("=" * 80)
print("PROFILE RESULTS - SORTED BY CUMULATIVE TIME (what calls what)")
print("=" * 80)
print(s.getvalue())

# Também ordenar por tempo interno (hot loop)
s2 = io.StringIO()
ps2 = pstats.Stats(pr, stream=s2).sort_stats('time')
ps2.print_stats(30)
print("\n" + "=" * 80)
print("PROFILE RESULTS - SORTED BY INTERNAL TIME (hot loops)")
print("=" * 80)
print(s2.getvalue())

# Resumo simples
print("\n" + "=" * 80)
print("SUMMARY - TOP CULPRITS")
print("=" * 80)
stats = pstats.Stats(pr).sort_stats('cumulative')
print(f"Total function calls: {stats.total_calls}")
print(f"Total time: {stats.total_tt:.2f}s")
print("\nTop 10 by cumulative time:")
stats.print_stats(10)
