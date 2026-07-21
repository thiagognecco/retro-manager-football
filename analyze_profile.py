#!/usr/bin/env python3
"""
Analyze profiling data from cProfile to identify GPU candidates
"""

import pstats
import sys
from io import StringIO

def analyze_profile(profile_file='profile_stats'):
    """Load and analyze profile statistics"""

    stats = pstats.Stats(profile_file)
    stats.sort_stats('cumulative')

    # Get top functions by cumulative time
    print("\n" + "="*100)
    print("TOP 20 FUNCTIONS BY CUMULATIVE TIME")
    print("="*100)

    # Capture stats output
    stream = StringIO()
    stats.stream = stream
    stats.print_stats(20)

    print(stream.getvalue())

    # Get stats by module
    print("\n" + "="*100)
    print("ANALYSIS BY COMPONENT")
    print("="*100)

    stats.sort_stats('cumulative')
    all_stats = stats.stats

    # Categorize by module
    categories = {
        'Spatial/Grid': [],
        'Tactical/Graph': [],
        'Behaviors': [],
        'Movement': [],
        'Events': [],
        'Physics': [],
        'Other': []
    }

    for func_key, func_stats in all_stats.items():
        func_name = func_key[2]
        module = func_key[0]
        cumtime = func_stats[3]  # cumulative time

        if any(x in func_name.lower() for x in ['spatial', 'grid', 'neighbor', 'proximity']):
            categories['Spatial/Grid'].append((func_name, cumtime))
        elif any(x in func_name.lower() for x in ['tactical', 'graph', 'prediction', 'gnn', 'model']):
            categories['Tactical/Graph'].append((func_name, cumtime))
        elif any(x in func_name.lower() for x in ['behavior', 'decision', 'action']):
            categories['Behaviors'].append((func_name, cumtime))
        elif any(x in func_name.lower() for x in ['move', 'position', 'velocity', 'path']):
            categories['Movement'].append((func_name, cumtime))
        elif any(x in func_name.lower() for x in ['event', 'card', 'injury', 'foul', 'corner']):
            categories['Events'].append((func_name, cumtime))
        elif any(x in func_name.lower() for x in ['collision', 'physics', 'force']):
            categories['Physics'].append((func_name, cumtime))
        else:
            categories['Other'].append((func_name, cumtime))

    # Print categorized analysis
    for category, funcs in categories.items():
        if funcs:
            total_time = sum(f[1] for f in funcs)
            print(f"\n{category}: {total_time:.2f}s total ({total_time/sum(sum(f[1] for f in funcs) for funcs in categories.values())*100:.1f}%)")
            for func, time in sorted(funcs, key=lambda x: x[1], reverse=True)[:5]:
                print(f"  - {func}: {time:.3f}s")

    # Summary for GPU decision
    print("\n" + "="*100)
    print("GPU OPPORTUNITY ASSESSMENT")
    print("="*100)

    spatial_time = sum(f[1] for f in categories['Spatial/Grid'])
    tactical_time = sum(f[1] for f in categories['Tactical/Graph'])
    movement_time = sum(f[1] for f in categories['Movement'])
    behavior_time = sum(f[1] for f in categories['Behaviors'])
    event_time = sum(f[1] for f in categories['Events'])

    parallelizable = spatial_time + tactical_time + movement_time
    sequential = behavior_time + event_time
    total = parallelizable + sequential

    print(f"\nParallelizable (GPU candidates):")
    print(f"  - Spatial/Grid queries: {spatial_time:.2f}s ({spatial_time/total*100:.1f}%)")
    print(f"  - Tactical/Graph: {tactical_time:.2f}s ({tactical_time/total*100:.1f}%)")
    print(f"  - Movement: {movement_time:.2f}s ({movement_time/total*100:.1f}%)")
    print(f"  TOTAL PARALLELIZABLE: {parallelizable:.2f}s ({parallelizable/total*100:.1f}%)")

    print(f"\nSequential (CPU only):")
    print(f"  - Behaviors: {behavior_time:.2f}s ({behavior_time/total*100:.1f}%)")
    print(f"  - Events: {event_time:.2f}s ({event_time/total*100:.1f}%)")
    print(f"  TOTAL SEQUENTIAL: {sequential:.2f}s ({sequential/total*100:.1f}%)")

    print(f"\nGPU SPEEDUP ESTIMATE:")
    if parallelizable / total > 0.4:
        print(f"  ✅ Excellent GPU candidate (>{parallelizable/total*100:.0f}% parallelizable)")
        print(f"  Expected speedup: 2-3x (GPU can accelerate {parallelizable/total*100:.0f}% of work)")
    elif parallelizable / total > 0.3:
        print(f"  ⚠️  Marginal GPU benefit ({parallelizable/total*100:.0f}% parallelizable)")
        print(f"  Expected speedup: 1.3-1.5x")
    else:
        print(f"  ❌ Poor GPU candidate (<{parallelizable/total*100:.0f}% parallelizable)")
        print(f"  CPU-only is sufficient")

if __name__ == '__main__':
    analyze_profile()
