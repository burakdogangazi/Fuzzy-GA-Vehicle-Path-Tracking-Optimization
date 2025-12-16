# BMProje — Fuzzy Logic + Genetic Algorithm Vehicle Optimization

**Short description:** This project uses fuzzy logic controllers (angle & velocity) optimized by a genetic algorithm (GA) to train a simulated vehicle to follow generated paths. It includes tools to run training/benchmarks and an interactive simulation viewer.

---

## What it is
- A research/experimental codebase combining **fuzzy control** and **GA optimization** to produce controllers that steer a vehicle along predefined paths (`convex` and `sin`).
- Provides: benchmarking scripts, a simulation viewer, fuzzy system generator, and evaluation utilities.

## Important files
- `src/genetic_algorithm.py` — GA implementation and chromosome representation
- `src/ga_fitness.py` — fitness evaluation and GA↔simulation bridge
- `src/fuzzy.py` — fuzzy system primitives (MFs, rules, defuzzification)
- `src/fuzzy_generator.py` — builds random fuzzy systems / rules
- `src/decoder.py` — converts sensor measurements → fuzzy inputs → movement commands
- `src/vehicle.py` — vehicle dynamics and sensors
- `src/simulation.py` — pygame-based visual simulator
- `src/benchmark_subprocess.py` — runs multiple GA configurations and exports CSV reports
- `results/` — output directory (benchmark CSVs, simulation outputs)

---

## Dependencies
Minimum recommended:

- Python 3.8+
- numpy
- pygame
- matplotlib (optional, for plotting fuzzy diagrams)
- opencv-python (optional, for saving simulation videos)

Install (example):

```bash
python -m pip install numpy pygame matplotlib opencv-python
```

(You may prefer to create a `requirements.txt` and install via `pip install -r requirements.txt`.)

---

## Run the interactive simulation
Open a terminal at project root and:

```bash
# Run pretrained on convex polygon
python src/simulation.py --polygon convex

# Save video of the run
python src/simulation.py --polygon sin --save-video
```

What you see on the right panel (text):
- **Sensor inputs:** left / front / right distances (pixels), scaled inside the decoder.  
- **FUZZY INPUTS:** membership degrees `mi` for each input MF (format: `mi | MF_name | [(x,y), ...]`) — the MF shape shows 2 points for edge MFs (triangle) and 4 points for middle MFs (trapezoid).  
- **FUZZY OUTPUTS:** output MFs with their `mi` values.  
- **Solutions:** `angle solution` and `velocity solution` are defuzzified outputs (centroid method).

---

## Run the benchmark suite
The benchmark runner executes multiple GA strategies across both paths and writes CSV reports.

```bash
python src/benchmark_subprocess.py
```

Outputs are written to `results/benchmark/benchmark_YYYYMMDD_HHMMSS/` and include:
- `benchmark_detailed_runs.csv` — per-run metrics
- `benchmark_strategy_comparison.csv` — metrics by strategy
- `benchmark_path_comparison.csv` — metrics by path
- `benchmark_summary_statistics.csv` — aggregated stats
- `benchmark_summary_report.txt` — readable summary

### Strategies (defined in `benchmark_subprocess.py`)
- `aggressive_exploration` — high mutation, lower population; favors exploration
- `balanced_strategy` — moderate params; balance of exploration/exploitation
- `conservative_exploitation` — large population, low mutation, higher elitism; fine‑tuning, risk of local minima

---

## Fuzzy & GA notes
- Defuzzification uses the **centroid** (weighted average of MF centers) implemented in `src/fuzzy.py`. If total membership is zero, solution = 0.
- MF shapes: **edge MFs** are represented with 2 points (triangle); **middle MFs** use 4 points (trapezoid). See `src/fuzzy_generator.py` for the generator logic.
- The GA evaluates controllers by running the simulation, collects: fitness, total distance, crash/idle flags, and stability metrics.

---

## Quick tips
- Benchmarks can be long; reduce runs / population sizes in `benchmark_subprocess.py` if you want faster tests.
- To inspect a trained fuzzy system, use the `simulation` runner with `--save-video` and inspect the right panel output or load the pickled fuzzy system at `constants.PRETRAINED_FUZZY_PATH`.

---

## Contributing & License
- Feel free to open issues or submit PRs. Add tests and small, focused changes.  
- License: add your preferred license file (`LICENSE`) to the repository.

---

If you want, I can:
- add a `requirements.txt`,
- add usage examples to `README.md`, or
- insert explanatory comments into `decoder.get_info()` and `simulation.draw_screen()` to make the on-screen text clearer.

Pick one and I’ll implement it.
