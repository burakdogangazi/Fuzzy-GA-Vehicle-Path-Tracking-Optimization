# Workflow Diagram - Benchmark Subprocess

## Execution Flow

```
python benchmark_subprocess.py
    |
    v
[INITIALIZATION]
    |-- Load GA_STRATEGIES (3 strategies)
    |-- Setup output directory
    |-- Create result containers
    |
    v
[TRAINING LOOP]
    |
    +-- FOR EACH PATH (convex, sin)
    |   |
    |   +-- FOR EACH STRATEGY (aggressive, balanced, conservative)
    |   |   |
    |   |   +-- FOR EACH RUN (1, 2, 3)
    |   |       |
    |   |       [TRAIN GA]
    |   |       |-- Set global GA parameters
    |   |       |-- Initialize population (500/1000/1500)
    |   |       |-- Evolution loop (15/20/30 generations)
    |   |       |   |-- Selection
    |   |       |   |-- Crossover
    |   |       |   |-- Mutation
    |   |       |   |-- Elitism
    |   |       |-- Get best chromosome
    |   |       |
    |   |       [EVALUATE VEHICLE]
    |   |       |-- Run vehicle simulation
    |   |       |-- Collect metrics
    |   |       |   |-- fitness_value
    |   |       |   |-- total_distance
    |   |       |   |-- crashed
    |   |       |   |-- success_rate
    |   |       |   |-- etc.
    |   |       |
    |   |       [STORE METRICS]
    |   |       |-- Create BenchmarkMetrics object
    |   |       |-- Add to results list
    |
    v
[SUMMARIZATION]
    |-- Calculate summary stats by strategy-path
    |-- Compute averages, std dev, min/max
    |
    v
[EXPORT PHASE]
    |
    +-- Export 1: benchmark_detailed_runs_*.csv
    |   |-- All 18 runs with all metrics
    |   |-- One row per run
    |
    +-- Export 2: benchmark_strategy_comparison_*.csv
    |   |-- Strategy comparison across paths
    |   |-- Metrics: fitness, distance, success_rate, etc.
    |   |-- Compare: convex vs sin for each strategy
    |
    +-- Export 3: benchmark_path_comparison_*.csv
    |   |-- Path comparison across strategies
    |   |-- Metrics: same as above
    |   |-- Compare: all 3 strategies for each path
    |
    +-- Export 4: benchmark_summary_statistics_*.csv
    |   |-- One row per strategy-path combo (6 rows)
    |   |-- Summary stats: avg, std, min, max, rates
    |
    v
[CONSOLE SUMMARY]
    |-- Print detailed analysis
    |-- Print best strategy per path
    |
    v
[COMPLETE]
```

## File Structure After Execution

```
src/
  benchmark_subprocess.py      [MAIN SCRIPT]
  |
  results/
    benchmark/
      benchmark_detailed_runs_20251125_143045.csv          [CSV 1]
      benchmark_strategy_comparison_20251125_143045.csv    [CSV 2]
      benchmark_path_comparison_20251125_143045.csv        [CSV 3]
      benchmark_summary_statistics_20251125_143045.csv     [CSV 4]
```

## Data Flow

```
GA Training
    |
    v
Best Chromosome (Fitness)
    |
    v
Vehicle Simulation
    |
    v
Metrics Collection
    |-- fitness_value
    |-- total_distance
    |-- crashed (yes/no)
    |-- success_rate
    |-- crash_rate
    |-- efficiency
    |-- left_right_balance
    |-- steering_stability
    |
    v
BenchmarkMetrics Object
    |
    v
CSV Export
    |
    v
4 Comprehensive Reports
```

## 18 Runs Breakdown

```
AGGRESSIVE_EXPLORATION (3 strategies × 2 paths × 3 runs = 18 total)
├─ Convex Path
│  ├─ Run 1 → metrics → CSV row 1
│  ├─ Run 2 → metrics → CSV row 2
│  └─ Run 3 → metrics → CSV row 3
└─ Sin Path
   ├─ Run 1 → metrics → CSV row 4
   ├─ Run 2 → metrics → CSV row 5
   └─ Run 3 → metrics → CSV row 6

BALANCED_STRATEGY
├─ Convex Path
│  ├─ Run 1 → metrics → CSV row 7
│  ├─ Run 2 → metrics → CSV row 8
│  └─ Run 3 → metrics → CSV row 9
└─ Sin Path
   ├─ Run 1 → metrics → CSV row 10
   ├─ Run 2 → metrics → CSV row 11
   └─ Run 3 → metrics → CSV row 12

CONSERVATIVE_EXPLOITATION
├─ Convex Path
│  ├─ Run 1 → metrics → CSV row 13
│  ├─ Run 2 → metrics → CSV row 14
│  └─ Run 3 → metrics → CSV row 15
└─ Sin Path
   ├─ Run 1 → metrics → CSV row 16
   ├─ Run 2 → metrics → CSV row 17
   └─ Run 3 → metrics → CSV row 18

TOTAL: 18 GA Trainings + 18 Vehicle Simulations
```

## CSV Files Summary

```
CSV 1: benchmark_detailed_runs_*.csv
┌─────────────────────────────────────┐
│ 18 Rows × 20 Columns                │
│ ─────────────────────────────────── │
│ strategy  path  run_id  fitness     │
│ ─────────────────────────────────── │
│ aggressive convex 1    0.2534      │
│ aggressive convex 2    0.2512      │
│ aggressive convex 3    0.2456      │
│ aggressive sin    1    0.3123      │
│ aggressive sin    2    0.3045      │
│ aggressive sin    3    0.3001      │
│ balanced   convex 1    0.1845      │
│ ...                                 │
└─────────────────────────────────────┘

CSV 2: benchmark_strategy_comparison_*.csv
┌──────────────────────────────────────────┐
│ Strategy Comparison (Metrics × Strategy) │
│ ────────────────────────────────────────│
│ metric           strategy       convex   sin    winner
│ ────────────────────────────────────────│
│ Fitness          aggressive     0.25    0.31   convex
│ Fitness          balanced       0.18    0.24   convex
│ Fitness          conservative   0.16    0.19   convex
│ Success Rate(%)  aggressive     100.0   66.7   convex
│ ...                                         │
└──────────────────────────────────────────┘

CSV 3: benchmark_path_comparison_*.csv
┌────────────────────────────────────────────┐
│ Path Comparison (Metrics × Path)           │
│ ────────────────────────────────────────── │
│ metric           path    aggressive balanced conservative best
│ ────────────────────────────────────────── │
│ Fitness          convex  0.25     0.18    0.16        conservative
│ Fitness          sin     0.31     0.24    0.19        conservative
│ Success Rate(%)  convex  100.0    100.0   100.0       balanced
│ ...                                                    │
└────────────────────────────────────────────┘

CSV 4: benchmark_summary_statistics_*.csv
┌─────────────────────────────────────────────┐
│ Summary Stats (6 Rows = 3 strat × 2 paths)  │
│ ─────────────────────────────────────────── │
│ strategy            path    num  avg_fitness crash_rate
│ ─────────────────────────────────────────── │
│ aggressive_exp      convex  3    0.2534     0.0
│ aggressive_exp      sin     3    0.3123     33.3
│ balanced_strategy   convex  3    0.1845     0.0
│ balanced_strategy   sin     3    0.2450     0.0
│ conservative_expl   convex  3    0.1567     0.0
│ conservative_expl   sin     3    0.1923     0.0
└─────────────────────────────────────────────┘
```

## Timeline

```
Start
  |
  |-- [0:00] Aggressive × Convex (3 runs) ....... 30 min
  |
  |-- [0:30] Aggressive × Sin (3 runs) ......... 30 min
  |
  |-- [1:00] Balanced × Convex (3 runs) ....... 45 min
  |
  |-- [1:45] Balanced × Sin (3 runs) .......... 45 min
  |
  |-- [2:30] Conservative × Convex (3 runs) .. 60 min
  |
  |-- [3:30] Conservative × Sin (3 runs) ..... 60 min
  |
  |-- [4:30] Export & Summary ................. 5 min
  |
End [4:35] Total: ~3-4 hours
```

## Metrics Hierarchy

```
BenchmarkMetrics (18 instances total)
├─ Configuration
│  ├─ population_size
│  ├─ max_iterations
│  ├─ elitism_ratio
│  └─ mutation_rate
├─ GA Results
│  └─ fitness_value
├─ Vehicle Simulation
│  ├─ total_distance
│  ├─ iterations_completed
│  ├─ crashed
│  ├─ idle
│  └─ collision_penalty
└─ Derived Metrics
   ├─ success_rate
   ├─ efficiency_score
   ├─ left_right_balance
   └─ steering_stability
```

## Comparison Logic

```
Strategy Comparison
├─ For each strategy: aggressive, balanced, conservative
│  ├─ Get metrics for path=convex
│  ├─ Get metrics for path=sin
│  ├─ Compare: convex_avg vs sin_avg
│  └─ Calculate: win_margin = |diff| / max_value × 100%

Path Comparison
├─ For each path: convex, sin
│  ├─ Get metrics for strategy=aggressive
│  ├─ Get metrics for strategy=balanced
│  ├─ Get metrics for strategy=conservative
│  └─ Find: best_strategy = min(values) for fitness

Summary Statistics
├─ Group metrics by (strategy, path)
├─ For each group:
│  ├─ avg = mean(fitness_values)
│  ├─ std = stddev(fitness_values)
│  ├─ min/max = min/max(fitness_values)
│  ├─ success_rate = count(success) / total × 100%
│  └─ crash_rate = count(crash) / total × 100%
```

This is the complete architecture! Ready to run!
