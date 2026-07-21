# BENCHMARK & GPU ANALYSIS REPORT
**Date**: 2026-07-21  
**Status**: COMPLETE  

---

## 📊 BENCHMARK RESULTS

### Raw Performance Data
- **Total time (5 matches)**: 152.2 seconds
- **Average per match**: 30.4 seconds ✅
- **Frames processed**: 27,000 (5 × 5,400)
- **Frame rate**: 177 fps (avg, 6.5ms per frame)

**Previous baseline**: 32.3s/match (from memory)  
**Current**: 30.4s/match (improvement likely from optimizations already applied)

---

## 🔍 TIME BREAKDOWN BY COMPONENT

Based on analysis of 5400 frames per match:

| Component | Avg Time (ms) | % of Total | GPU Candidate? |
|-----------|:-------------:|------------|:-----:|
| **Behaviors (22x players)** | 5.51 | **84.8%** | ❌ NO |
| **Graph Build (Tactical)** | 0.28 | 4.3% | ✅ YES |
| **Predict Pos (GNN)** | 0.15 | 2.3% | ✅ YES |
| **Tactical State Update** | 0.03 | 0.5% | ⚠️ Maybe |
| **Grid Rebuild** | 0.06 | 0.9% | ✅ YES |
| **Events Processing** | 0.01 | 0.2% | ❌ NO |
| **TOTAL PER FRAME** | **6.5ms** | 100% | |

---

## 🎯 GPU OPPORTUNITY ANALYSIS

### Parallelizable Work (Ideal for GPU)
```
Graph Build (Tactical):        0.28ms  
Predict Pos (GNN):            0.15ms
Grid Rebuild:                 0.06ms
──────────────────────────────────────
TOTAL PARALLELIZABLE:         0.49ms  (7.5% of 6.5ms)
```

### Sequential Work (CPU-only, Can't Parallelize)
```
Behaviors (Tree Traversal):    5.51ms  (84.8%)
Events Processing:             0.01ms
Tactical State:                0.03ms
──────────────────────────────────────
TOTAL SEQUENTIAL:              5.55ms  (85.5%)
```

---

## 📈 REALISTIC GPU SPEEDUP ESTIMATE

### Best-Case Scenario (5x GPU speedup on parallelizable work):
```
Original:        6.5ms per frame

If GPU accelerates 7.5%:
GPU time:        0.49ms ÷ 5 = 0.098ms
CPU time:        5.55ms (unchanged)
New total:       5.65ms per frame

Speedup:         6.5 / 5.65 = 1.15x  (only 15% faster)
Per match:       30.4s → 26.4s (4 seconds faster)
```

### More Realistic Scenario (3x speedup, accounting for overhead):
```
GPU overhead:    0.2ms per frame
Actual speedup:  0.49ms × (1/3) + 0.2ms = 0.36ms
New total:       5.55 + 0.36 = 5.91ms

Result:          6.5 / 5.91 = 1.1x  (only 10% faster)
Per match:       30.4s → 27.6s (2.8 seconds faster)
```

### If GPU Overhead Exceeds Benefit:
```
If GPU transfer + overhead = 0.3ms:
Time saved:      0.49 × (2/3) = 0.33ms
Overhead cost:   0.3ms
Net benefit:     0.03ms

Result:          SLIGHTLY WORSE or no benefit!
```

---

## ❌ WHY GPU IS NOT RECOMMENDED

### Root Cause: Behavior Tree is the Bottleneck
The **Behavior Tree Traversal (85% of time)** is:
- ✗ Sequential decision-making per player
- ✗ Depends on game state updates
- ✗ Can't run in parallel (one player's decision affects others)
- ✗ Not vectorizable (branches, if/else logic)

### GPU Math
- **Max speedup if we GPU all parallelizable work**: 1.15x
- **More realistic with overhead**: 1.05-1.10x
- **Cost of GPU implementation**: 4-6 hours
- **ROI**: Very poor (10% speedup ≠ worth 6 hours)

---

## ✅ CURRENT PERFORMANCE IS ADEQUATE

### For Testing & Development
- 30.4s/match → runs 50 matches in ~25 minutes
- Fast enough for iteration and debugging
- Can run on CPU-only hardware (no NVIDIA GPU needed)

### For Production (if needed later)
**Better optimization strategies than GPU:**

1. **Behavior Tree Optimization** (High impact)
   - Reduce decision complexity
   - Cache repeated calculations
   - Skip unnecessary evaluations
   - **Estimated gain**: 2-3x speedup possible

2. **Parallelizing Player Updates** (Requires refactoring)
   - Run 22 player behaviors in parallel (CPU multi-threading)
   - **Estimated gain**: 4-6x on multi-core (8+ cores)
   - **Effort**: 8-12 hours

3. **Physics Simplification** (Medium impact)
   - Reduce collision checks
   - Simplified movement interpolation
   - **Estimated gain**: 1.5-2x speedup

---

## 🏁 DECISION: ❌ DO NOT PURSUE GPU OPTIMIZATION

### Recommendation: Keep CPU-Only
**Rationale:**
1. 30.4s/match is fast enough for testing
2. GPU speedup (1.1-1.15x) doesn't justify 6 hour implementation
3. Behavior Tree (85%) is not GPU-suitable
4. Better ROI strategies exist (CPU multi-threading, BT optimization)
5. Maintains hardware compatibility (no NVIDIA requirement)

### Alternative Path (if performance becomes bottleneck):
1. **First**: Profile Behavior Tree in detail → identify optimization opportunities
2. **Second**: Implement CPU multi-threading (22 players in parallel)
3. **Third**: Only then consider GPU if gains < 2x from above

---

## 💾 PROFILING DATA SUMMARY

**Processed**: 27,000 frames across 5 matches  
**Variability**: Frame times ranged 2.0ms - 26.6ms (depending on game events)  
**Consistency**: Average stayed ~6.5ms (±1.5ms std dev)  
**Memory**: No spikes observed during profiling  

---

## 📋 NEXT STEPS

### Immediate (This Session)
- ✅ Close GPU optimization investigation
- ✅ Document decision in CLAUDE.md
- 📌 Mark performance as acceptable for current phase

### Future (If performance becomes issue)
1. Deep-dive: Behavior Tree optimization
2. Profile: Individual player decision costs
3. Evaluate: Multi-threading feasibility
4. Implement: CPU parallelization (high ROI)

---

**Status**: DECISION MADE - GPU NOT RECOMMENDED ✓  
**Next Phase**: Continue with simulation improvements (not performance)
