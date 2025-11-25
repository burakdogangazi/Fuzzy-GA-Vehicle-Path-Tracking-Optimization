# Benchmark Subprocess Runner - Comprehensive Guide

## Overview

**`benchmark_subprocess.py`** is a non-invasive benchmark runner for comprehensive GA strategy comparison. It tests three different genetic algorithm strategies on two vehicle navigation paths and generates **4 detailed CSV reports** with complete metrics.

**Approach:** Direct API calls (similar logic to your `bench_runner.py` but using direct GA function calls for accuracy)

---

## Strategy Configurations

### 1. **AGGRESSIVE_EXPLORATION** 🚀
- **Character:** High mutation, high diversity
- **Parameters:**
  - Population: 500
  - Generations: 15
  - Mutation Rate: 0.25 (25% - very high)
  - Elitism: 0.02 (2%)
  - Mutation Span: 3
  - Tournament Size: 3
- **Use Case:** When you want to explore the solution space broadly
- **Runs per path:** 3

### 2. **BALANCED_STRATEGY** ⚖️
- **Character:** Moderate exploration-exploitation balance
- **Parameters:**
  - Population: 1000
  - Generations: 20
  - Mutation Rate: 0.1 (10% - moderate)
  - Elitism: 0.05 (5%)
  - Mutation Span: 2
  - Tournament Size: 5
- **Use Case:** General-purpose optimization
- **Runs per path:** 3

### 3. **CONSERVATIVE_EXPLOITATION** 🎯
- **Character:** Low mutation, strong convergence
- **Parameters:**
  - Population: 1500
  - Generations: 30
  - Mutation Rate: 0.05 (5% - low)
  - Elitism: 0.15 (15%)
  - Mutation Span: 1
  - Tournament Size: 7
- **Use Case:** When you want high-quality solutions through exploitation
- **Runs per path:** 3

---

## Paths

### **CONVEX** 🔷
- Simple geometric polygon
- Predictable, easier for GA to optimize
- Good baseline for strategy comparison

### **SIN** 〰️
- Complex sinuous path
- More challenging, tests GA robustness
- Distinguishes between strategies more clearly

---

## Execution

```bash
cd src/
python benchmark_subprocess.py
```

**Expected Runtime:**
- Total Runs: 3 strategies × 2 paths × 3 runs = 18 trainings
- Per training: ~10-30 minutes (depends on parameters)
- **Total: ~5-10 hours** (depending on system performance)

---

## Output Files

All results are saved to: `src/results/benchmark/`

### **1. `benchmark_detailed_runs_*.csv`** 📊
Complete metrics for every single run.

**Columns:**
- `timestamp`: When run was executed
- `strategy`: Strategy name (aggressive_exploration, balanced_strategy, conservative_exploitation)
- `path`: Path used (convex, sin)
- `run_id`: Run number (1, 2, or 3)
- `population_size`: GA population size
- `max_iterations`: GA generations
- `elitism_ratio`: Elitism percentage
- `mutation_rate`: Mutation rate
- `mutation_span`: Mutation span
- `mutation_genom_rate`: Genome mutation rate
- `tournament_size`: Tournament size for selection
- `fitness_value`: **Final fitness after training** (lower is better)
- `total_distance`: Total distance vehicle traveled
- `iterations_completed`: Simulation iterations before crash/completion
- `crashed`: Did vehicle crash? (0 or 1)
- `idle`: Did vehicle get stuck? (0 or 1)
- `collision_penalty`: Penalty for collision
- `success_rate`: 1.0 if no crash/idle, 0.0 otherwise
- `efficiency_score`: Distance per unit fitness
- `left_right_balance`: Balance between left/right sensor readings
- `steering_stability`: Stability of steering angles

**Example Row:**
```
2025-11-25 14:30:45, aggressive_exploration, convex, 1, 500, 15, 0.02, 0.25, 3, 0.15, 3, 0.2456, 2340.15, 1200, 0, 0, 0.0, 1.0, 9523.47, 0.1234, 0.0567
```

---

### **2. `benchmark_strategy_comparison_*.csv`** 📈
Compare strategies against each other on different paths.

**Structure:**
- Rows grouped by `metric` (Fitness, Distance, Success Rate, etc.)
- Within each metric, one row per strategy
- Compares `convex` vs `sin` paths for each strategy

**Example:**
```
metric,strategy,convex_avg,convex_std,sin_avg,sin_std,convex_min,convex_max,sin_min,sin_max,convex_better,win_margin
Fitness (lower is better),aggressive_exploration,0.2973,0.0128,0.3845,0.0245,0.2850,0.3150,0.3650,0.4100,Yes,22.70%
Fitness (lower is better),balanced_strategy,0.1845,0.0056,0.2450,0.0134,0.1789,0.1923,0.2340,0.2650,Yes,18.45%
Success Rate (%),aggressive_exploration,1.0,0.0,0.95,0.05,1.0,1.0,0.9,1.0,Yes,5.26%
```

**Interpretation:**
- `convex_avg`: Average metric value on convex path
- `convex_std`: Standard deviation on convex
- `convex_better`: Whether convex performed better
- `win_margin`: Performance improvement percentage

---

### **3. `benchmark_path_comparison_*.csv`** 🗺️
Compare paths against each other with different strategies.

**Structure:**
- Rows grouped by `metric`
- Within each metric, one row per path
- Compares all 3 strategies for each path

**Example:**
```
metric,path,aggressive_avg,balanced_avg,conservative_avg,aggressive_std,balanced_std,conservative_std,best_strategy,worst_strategy
Fitness (lower is better),convex,0.2973,0.1845,0.1234,0.0128,0.0056,0.0089,conservative_exploitation,aggressive_exploration
Fitness (lower is better),sin,0.3845,0.2450,0.1567,0.0245,0.0134,0.0145,conservative_exploitation,aggressive_exploration
Success Rate (%),convex,1.0,1.0,1.0,0.0,0.0,0.0,balanced_strategy,aggressive_exploration
```

**Interpretation:**
- Which strategy works best on each path
- Conservative typically better for fitness
- Aggressive might crash more often
- Balanced is middle ground

---

### **4. `benchmark_summary_statistics_*.csv`** 📋
Overall summary statistics for each strategy-path combination.

**Columns:**
- `strategy`: Strategy name
- `path`: Path name
- `num_runs`: Number of runs (usually 3)
- `avg_fitness`: Average fitness across runs
- `std_fitness`: Standard deviation of fitness
- `min_fitness`: Best fitness achieved
- `max_fitness`: Worst fitness achieved
- `avg_distance`: Average distance traveled
- `avg_iterations`: Average iterations completed
- `success_rate_pct`: Percentage of successful runs
- `avg_efficiency`: Average efficiency score
- `crash_rate_pct`: Percentage of runs that crashed

**Example:**
```
strategy,path,num_runs,avg_fitness,std_fitness,min_fitness,max_fitness,avg_distance,avg_iterations,success_rate_pct,avg_efficiency,crash_rate_pct
aggressive_exploration,convex,3,0.2973,0.0128,0.2850,0.3150,2340.15,1200.0,100.0,7873.45,0.0
aggressive_exploration,sin,3,0.3845,0.0245,0.3650,0.4100,2156.40,1050.0,66.7,5643.12,33.3
balanced_strategy,convex,3,0.1845,0.0056,0.1789,0.1923,3450.20,1500.0,100.0,18726.34,0.0
conservative_exploitation,sin,3,0.1567,0.0145,0.1450,0.1750,3890.60,1600.0,100.0,24821.15,0.0
```

---

## Key Metrics Explained

### **Fitness** (Lower is Better)
- Directly from GA optimization
- Measures how well vehicle follows path with minimal deviations
- Lower = better path following

### **Distance**
- Total pixels traveled by vehicle
- Higher = vehicle made more progress
- Correlates with longer survival time

### **Success Rate**
- Percentage of runs that didn't crash or idle
- 100% = never crashed
- 0% = always crashed

### **Efficiency Score**
- `Distance / Fitness`
- Measures how much distance gained per unit of fitness optimization
- Higher = better bang for your buck

### **Left/Right Balance**
- How equal the left and right sensor readings are
- Lower = better centered path following
- Indicates vehicle stays in middle of path

### **Steering Stability**
- Standard deviation of steering angle changes
- Lower = smoother steering, fewer corrections
- Higher = jerky, unstable vehicle control

---

## How to Read the Results

### **Best Strategy Overall?**
Look at `benchmark_summary_statistics_*.csv`:
- Find row with lowest `avg_fitness`
- That strategy × path combination is best

### **Path Difficulty?**
Compare metrics for same strategy across paths:
- `convex` vs `sin` in strategy comparison CSV
- Which path has worse fitness?
- Sin typically harder (higher fitness values)

### **Strategy Trade-offs?**
```
Aggressive:    Low fitness (good), but might crash (lower success rate)
Balanced:      Middle fitness, reliable, good success rate
Conservative:  High fitness cost (good), reliable, high quality
```

### **Reliability?**
- High `std_fitness` = inconsistent strategy
- Low `std_fitness` = consistent strategy
- High `success_rate_pct` = robust strategy

---

## Example Analysis Workflow

```
1. Open benchmark_summary_statistics_*.csv
   ↓ Find strategy with best (lowest) avg_fitness
   
2. Open benchmark_path_comparison_*.csv
   ↓ Which path easier for that strategy?
   ↓ Convex or Sin?
   
3. Open benchmark_detailed_runs_*.csv
   ↓ Look at individual runs for best combo
   ↓ Check for outliers/crashes
   
4. Open benchmark_strategy_comparison_*.csv
   ↓ Confirm fitness gap between strategies
   ↓ Check if gap consistent across paths
```

---

## Academic Insights

### **When to Use Each Strategy:**

1. **AGGRESSIVE_EXPLORATION**
   - Useful for initial broad exploration
   - May find novel solutions
   - Higher risk of instability
   - Good for unknown problem spaces

2. **BALANCED_STRATEGY**
   - Recommended for most scenarios
   - Reliable, reproducible results
   - Good balance of speed and quality
   - Production-grade choice

3. **CONSERVATIVE_EXPLOITATION**
   - When you need the absolute best solution
   - Time is not a constraint
   - Willing to trade exploration for quality
   - Good for fine-tuning

---

## Technical Details

### **Fitness Calculation**
Handled by `ga_fitness.evaluate()`:
- CTE (Cross-Track Error): How far from path
- Steering smoothness
- Speed consistency
- Overall path following quality

### **Vehicle Simulation**
Each trained chromosome runs through simulation:
- Sensors: left, front, right distance
- Fuzzy logic: converts sensors to movement
- Car physics: updates position/angle
- Stops if: crash detected OR max iterations reached

### **Metrics Collection**
For each run:
1. GA trains best chromosome
2. Best chromosome runs vehicle simulation
3. All metrics recorded during simulation
4. Results appended to CSV

---

## Troubleshooting

### **Runs taking too long?**
- Reduce `max_iterations` in GA_STRATEGIES
- Reduce `runs` count (now 3, try 1)
- Reduce population sizes

### **All crashes, no success?**
- Check path loading (convex/sin params)
- Check vehicle physics
- Check fuzzy logic implementation

### **Huge fitness values?**
- Check GA_FITNESS penalty calculations
- May indicate path following is very poor
- Check if distance values make sense

### **CSV not generating?**
- Check `src/results/benchmark/` directory exists
- Check file permissions
- Check for Python errors in console

---

## Files Used

**Read from:**
- `genetic_algorithm.py`: GA implementation
- `ga_fitness.py`: Fitness evaluation
- `vehicle.py`: Vehicle simulation
- `decoder.py`: Fuzzy logic to movement conversion
- `utils/load_path.py`: Path loading (convex/sin)
- `utils/constants.py`: Constants

**Write to:**
- `src/results/benchmark/benchmark_detailed_runs_*.csv`
- `src/results/benchmark/benchmark_strategy_comparison_*.csv`
- `src/results/benchmark/benchmark_path_comparison_*.csv`
- `src/results/benchmark/benchmark_summary_statistics_*.csv`

---

## Next Steps

1. Run the benchmark
2. Analyze the 4 CSV files
3. Identify best strategy-path combination
4. Consider fine-tuning parameters if needed
5. Generate plots from CSV data for presentation

Good luck! 🚀
