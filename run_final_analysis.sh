#!/bin/bash
# Final Analysis Runner - Executes when TIER 50-match benchmark completes

cd "C:\Users\gnecc\Documents\Footbal manager"

echo "=================================="
echo "TIER 2 BENCHMARK ANALYSIS - START"
echo "=================================="

# Run analysis
python analyze_tier2_results.py

echo ""
echo "=================================="
echo "Analysis complete!"
echo "Results saved to BENCHMARK_ANALYSIS_21_07.md"
echo "=================================="
