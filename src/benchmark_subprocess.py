"""
Non-invasive Benchmark Runner for Fuzzy Logic Vehicle GA Optimization
Subprocess approach - runs genetic_algorithm.py multiple times with different strategies
Generates 4 comprehensive CSV reports

Strategy Comparison:
  1. AGGRESSIVE_EXPLORATION: High mutation, high diversity
  2. BALANCED_STRATEGY: Moderate exploration-exploitation  
  3. CONSERVATIVE_EXPLOITATION: Low mutation, strong convergence

Paths:
  - convex: Simple geometric polygon
  - sin: Complex sinuous path

Output:
  1. benchmark_detailed_runs_*.csv - All individual runs with metrics
  2. benchmark_strategy_comparison_*.csv - Strategies vs paths
  3. benchmark_path_comparison_*.csv - Paths vs strategies
  4. benchmark_summary_statistics_*.csv - Overall summary statistics
"""

import os
import sys
import csv
import json
import shutil
import pickle
import time
import random
from datetime import datetime
from pathlib import Path

# Import directly to check parameters
import genetic_algorithm as ga
import ga_fitness
from utils import load_path as lp
from utils import constants
import vehicle
import decoder


# ============================================================================
# BENCHMARK CONFIGURATION - 3 STRATEGIES × 2 PATHS
# ============================================================================

GA_STRATEGIES = {
    'aggressive_exploration': {
        'name': 'Aggressive Exploration',
        'description': 'Small population, high mutation for rapid exploration, with enhanced stability to increase success rate.',
        'population_size': 350,      
        'max_iterations': 25,          
        'elitism_ratio': 0.03,         
        'mutation_rate': 0.33,         
        'mutation_span': 4,            
        'mutation_genom_rate': 0.22,   
        'tournament_size': 3,          
        'runs': 10,  
    },
    'balanced_strategy': {
        'name': 'Balanced Strategy',
        'description': 'A more robust balanced approach with a larger population and stronger selection for better overall performance.',
        'population_size': 700,       
        'max_iterations': 35,         
        'elitism_ratio': 0.10,         
        'mutation_rate': 0.15,         
        'mutation_span': 3,            
        'mutation_genom_rate': 0.10,   
        'tournament_size': 6,          
        'runs': 10,  
    },
    'conservative_exploitation': {
        'name': 'Conservative Exploitation',
        'description': 'Fine-tuning focus with carefully controlled mutation to reduce crash rate while maintaining high fitness.',
        'population_size': 1200,      
        'max_iterations': 45,         
        'elitism_ratio': 0.15,         
        'mutation_rate': 0.05,         
        'mutation_span': 2,            
        'mutation_genom_rate': 0.03,   
        'tournament_size': 8,          
        'runs': 10,  
    },
}

PATHS = ['convex', 'sin']

# Fieldnames for CSV
DETAILED_FIELDNAMES = [
    'timestamp', 'strategy', 'path', 'run_id',
    'population_size', 'max_iterations', 'elitism_ratio',
    'mutation_rate', 'mutation_span', 'mutation_genom_rate', 'tournament_size',
    'fitness_value', 'total_distance', 'iterations_completed',
    'crashed', 'idle', 'collision_penalty', 'success_rate', 'efficiency_score',
    'left_right_balance', 'steering_stability',
]

STRATEGY_FIELDNAMES = [
    'metric', 'strategy', 'convex_avg', 'convex_std', 'sin_avg', 'sin_std',
    'convex_min', 'convex_max', 'sin_min', 'sin_max',
    'convex_better', 'win_margin',
]

PATH_FIELDNAMES = [
    'metric', 'path', 'aggressive_avg', 'balanced_avg', 'conservative_avg',
    'aggressive_std', 'balanced_std', 'conservative_std',
    'best_strategy', 'worst_strategy',
]

SUMMARY_FIELDNAMES = [
    'strategy', 'path', 'num_runs', 'avg_fitness', 'std_fitness',
    'min_fitness', 'max_fitness', 'avg_distance', 'avg_iterations',
    'success_rate_pct', 'avg_efficiency', 'crash_rate_pct',
]


# ============================================================================
# METRICS COLLECTION CLASS
# ============================================================================

class BenchmarkMetrics:
    """Stores metrics from a single training run"""
    
    def __init__(self, strategy, path, run_id):
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.strategy = strategy
        self.path = path
        self.run_id = run_id
        
        # GA Configuration
        self.population_size = 0
        self.max_iterations = 0
        self.elitism_ratio = 0.0
        self.mutation_rate = 0.0
        self.mutation_span = 0
        self.mutation_genom_rate = 0.0
        self.tournament_size = 0
        
        # Results from GA training
        self.fitness_value = None
        self.training_time = 0.0
        
        # Vehicle simulation metrics
        self.total_distance = 0.0
        self.iterations_completed = 0
        self.crashed = False
        self.idle = False
        self.collision_penalty = 0.0
        self.success_rate = 0.0
        self.efficiency_score = 0.0
        self.left_right_balance = 0.0
        self.steering_stability = 0.0
    
    def to_dict(self):
        """Convert to dictionary for CSV export"""
        return {
            'timestamp': self.timestamp,
            'strategy': self.strategy,
            'path': self.path,
            'run_id': self.run_id,
            'population_size': self.population_size,
            'max_iterations': self.max_iterations,
            'elitism_ratio': round(self.elitism_ratio, 4),
            'mutation_rate': round(self.mutation_rate, 4),
            'mutation_span': self.mutation_span,
            'mutation_genom_rate': round(self.mutation_genom_rate, 4),
            'tournament_size': self.tournament_size,
            'fitness_value': round(self.fitness_value, 6) if self.fitness_value else None,
            'total_distance': round(self.total_distance, 2),
            'iterations_completed': self.iterations_completed,
            'crashed': int(self.crashed),
            'idle': int(self.idle),
            'collision_penalty': round(self.collision_penalty, 2),
            'success_rate': round(self.success_rate, 4),
            'efficiency_score': round(self.efficiency_score, 4),
            'left_right_balance': round(self.left_right_balance, 4),
            'steering_stability': round(self.steering_stability, 4),
        }


# ============================================================================
# BENCHMARK RUNNER - SUBPROCESS APPROACH
# ============================================================================

class BenchmarkRunner:
    """Runs GA training using direct API (non-subprocess for accuracy)"""
    
    def __init__(self):
        self.results = []
        self.summary_by_strategy_path = {}
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir = self._setup_output_dir()
    
    def _setup_output_dir(self):
        """Create output directory for results with timestamp"""
        # Format: results/benchmark/benchmark_YYYYMMDD_HHMMSS/
        results_dir = os.path.join(os.path.dirname(__file__), 'results', 'benchmark', f'benchmark_{self.timestamp}')
        os.makedirs(results_dir, exist_ok=True)
        return results_dir
    
    def run_full_benchmark(self):
        """Execute complete benchmark across all strategies and paths"""
        print("\n" + "="*80)
        print("FUZZY LOGIC VEHICLE BENCHMARK - SUBPROCESS APPROACH")
        print("3 Strategies × 2 Paths × N Runs = Comprehensive Comparison")
        print("="*80)
        
        total_runs = sum(cfg['runs'] for cfg in GA_STRATEGIES.values()) * len(PATHS)
        print(f"\nTotal planned runs: {total_runs}")
        print(f"Paths: {', '.join(PATHS)}")
        print(f"Strategies: {', '.join(GA_STRATEGIES.keys())}")
        
        run_counter = 0
        
        for path_name in PATHS:
            print(f"\n{'='*80}")
            print(f"PATH: {path_name.upper()}")
            print(f"{'='*80}")
            
            road_matrix = self._load_path_matrix(path_name)
            
            for strategy_name, strategy_config in GA_STRATEGIES.items():
                print(f"\n{'*'*80}")
                print(f"STRATEGY: {strategy_config['name'].upper()}")
                print(f"Description: {strategy_config['description']}")
                print(f"Config: Pop={strategy_config['population_size']} Gen={strategy_config['max_iterations']} Mut={strategy_config['mutation_rate']}")
                print(f"{'*'*80}")
                
                for run_id in range(1, strategy_config['runs'] + 1):
                    run_counter += 1
                    print(f"\n[{run_counter}/{total_runs}] Running {strategy_name} on {path_name} (run {run_id}/{strategy_config['runs']})...")
                    
                    metrics = self.train_and_evaluate(
                        strategy_name, strategy_config, path_name, road_matrix, run_id
                    )
                    self.results.append(metrics)
        
        print("\n" + "="*80)
        print("TRAINING COMPLETE - GENERATING REPORTS")
        print("="*80)
        
        self.calculate_summary()
        self.export_all_reports()
    
    def _load_path_matrix(self, path_name):
        """Load road matrix for path"""
        if path_name == 'convex':
            path, road_matrix = lp.load_convex_params()
        else:
            path, road_matrix = lp.load_sin_params()
        return road_matrix
    
    def train_and_evaluate(self, strategy_name, strategy_config, path_name, road_matrix, run_id):
        """Train GA and evaluate performance"""
        metrics = BenchmarkMetrics(strategy_name, path_name, run_id)
        
        # Store configuration
        metrics.population_size = strategy_config['population_size']
        metrics.max_iterations = strategy_config['max_iterations']
        metrics.elitism_ratio = strategy_config['elitism_ratio']
        metrics.mutation_rate = strategy_config['mutation_rate']
        metrics.mutation_span = strategy_config['mutation_span']
        metrics.mutation_genom_rate = strategy_config['mutation_genom_rate']
        metrics.tournament_size = strategy_config['tournament_size']
        
        # Train GA
        start_time = time.time()
        best_chromosome = self._train_ga(strategy_config, road_matrix)
        metrics.training_time = time.time() - start_time
        metrics.fitness_value = best_chromosome.fitness
        
        print(f"  ✓ Training completed in {metrics.training_time:.2f}s | Fitness: {metrics.fitness_value:.6f}")
        
        # Evaluate vehicle performance
        self._evaluate_vehicle_performance(best_chromosome, road_matrix, metrics)
        
        return metrics
    
    def _train_ga(self, config, road_matrix):
        """Train genetic algorithm with given configuration"""
        # Set global GA parameters
        ga.road_matrix = road_matrix
        ga.memory = {}
        ga.POPULATION_SIZE = config['population_size']
        ga.MAX_ITERATIONS = config['max_iterations']
        ga.ELITISM_RATIO = config['elitism_ratio']
        ga.TOURNAMENT_SIZE = config['tournament_size']
        ga.MUTATION_RATE = config['mutation_rate']
        ga.MUTATION_SPAN = config['mutation_span']
        ga.MUTATION_GENOM_RATE = config['mutation_genom_rate']
        
        # Initialize population
        population = ga.init_population(config['population_size'])
        
        # GA loop
        for iteration in range(config['max_iterations']):
            population.sort()
            
            # Elitism
            elites_count = int(len(population) * config['elitism_ratio'])
            new_population = [population[i] for i in range(elites_count)]
            
            # Generate offspring
            for _ in range((config['population_size'] - elites_count) // 2):
                p1 = ga.select(population)
                p2 = ga.select(population)
                c1, c2 = ga.crossover(p1, p2)
                c1 = ga.mutate(c1)
                c2 = ga.mutate(c2)
                c1.update_fitness()
                c2.update_fitness()
                new_population.append(c1)
                new_population.append(c2)
            
            population = ga.np.array(new_population)
            
            best = ga.get_best_chromosome(population)
            if (iteration + 1) % 5 == 0 or iteration == config['max_iterations'] - 1:
                avg_fitness = ga.np.mean([c.fitness for c in population])
                print(f"    Gen {iteration+1:3d}/{config['max_iterations']}: Best={best.fitness:.6f} Avg={avg_fitness:.6f}")
        
        return ga.get_best_chromosome(population)
    
    def _evaluate_vehicle_performance(self, chromosome, road_matrix, metrics):
        """Evaluate trained chromosome vehicle performance"""
        car = vehicle.Car(constants.CAR_POS_X, constants.CAR_POS_Y, constants.CAR_ANGLE)
        dec = decoder.Decoder(chromosome.FSAngle, chromosome.FSVelocity, car)
        
        memory = {}
        iteration = 0
        total_distance = 0
        left_distances = []
        right_distances = []
        steering_angles = []
        crashed = False
        idle = False
        
        while iteration < ga_fitness.MAX_ITERATIONS:
            car.left_sensor_input, car.front_sensor_input, car.right_sensor_input = \
                ga_fitness.get_sensors(car, road_matrix, memory)
            
            left_distances.append(float(car.left_sensor_input))
            right_distances.append(float(car.right_sensor_input))
            
            ds, drot = dec.get_movement_params()
            car.update(ga_fitness.TIME_STEP, ds, drot)
            steering_angles.append(drot)
            
            iteration += 1
            total_distance += ds
            
            if car.is_collided2(road_matrix):
                crashed = True
                metrics.collision_penalty = 150
                break
            
            if car.is_idle(iteration):
                idle = True
                metrics.collision_penalty = 50
                break
        
        metrics.total_distance = total_distance
        metrics.iterations_completed = iteration
        metrics.crashed = crashed
        metrics.idle = idle
        metrics.max_iterations_reached = (iteration >= ga_fitness.MAX_ITERATIONS)
        metrics.success_rate = 0.0 if (crashed or idle) else 1.0
        metrics.efficiency_score = total_distance / (chromosome.fitness + 0.0001)
        
        # Calculate stability metrics
        if left_distances and right_distances:
            left_arr = ga.np.array(left_distances)
            right_arr = ga.np.array(right_distances)
            metrics.left_right_balance = float(ga.np.mean(ga.np.abs(left_arr - right_arr)))
        
        if steering_angles:
            metrics.steering_stability = float(ga.np.std(steering_angles))
        
        print(f"    Vehicle: Dist={metrics.total_distance:.1f} Iter={metrics.iterations_completed} Success={'✓' if metrics.success_rate > 0 else '✗'}")
    
    def calculate_summary(self):
        """Calculate summary statistics grouped by strategy and path"""
        self.summary_by_strategy_path = {}
        
        for strategy_name in GA_STRATEGIES.keys():
            self.summary_by_strategy_path[strategy_name] = {}
            
            for path_name in PATHS:
                relevant = [r for r in self.results if r.strategy == strategy_name and r.path == path_name]
                
                if relevant:
                    fitness_vals = [r.fitness_value for r in relevant]
                    distances = [r.total_distance for r in relevant]
                    iterations = [r.iterations_completed for r in relevant]
                    success_rates = [r.success_rate for r in relevant]
                    efficiency = [r.efficiency_score for r in relevant]
                    
                    self.summary_by_strategy_path[strategy_name][path_name] = {
                        'avg_fitness': ga.np.mean(fitness_vals),
                        'std_fitness': ga.np.std(fitness_vals),
                        'min_fitness': ga.np.min(fitness_vals),
                        'max_fitness': ga.np.max(fitness_vals),
                        'avg_distance': ga.np.mean(distances),
                        'avg_iterations': ga.np.mean(iterations),
                        'success_rate': ga.np.mean(success_rates),
                        'avg_efficiency': ga.np.mean(efficiency),
                        'crash_rate': 1.0 - ga.np.mean([1 if not r.crashed else 0 for r in relevant]),
                    }
    
    def export_all_reports(self):
        """Export all 4 CSV reports and summary"""
        # 1. Detailed runs
        self._export_detailed_runs()
        
        # 2. Strategy comparison
        self._export_strategy_comparison()
        
        # 3. Path comparison
        self._export_path_comparison()
        
        # 4. Summary statistics
        self._export_summary_statistics()
        
        # 5. Console summary (also saves to TXT)
        self.print_console_summary()
    
    def _export_detailed_runs(self):
        """Export detailed metrics for each run"""
        csv_path = os.path.join(self.output_dir, 'benchmark_detailed_runs.csv')
        
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=DETAILED_FIELDNAMES)
            writer.writeheader()
            for result in self.results:
                writer.writerow(result.to_dict())
        
        print(f"\n[OK] Detailed runs exported: {csv_path}")
    
    def _export_strategy_comparison(self):
        """Export strategy comparison across paths"""
        csv_path = os.path.join(self.output_dir, 'benchmark_strategy_comparison.csv')
        
        metrics_to_compare = [
            ('Fitness (lower is better)', 'avg_fitness'),
            ('Fitness Std Dev', 'std_fitness'),
            ('Avg Distance', 'avg_distance'),
            ('Success Rate (%)', 'success_rate'),
            ('Avg Efficiency', 'avg_efficiency'),
            ('Avg Iterations', 'avg_iterations'),
            ('Crash Rate (%)', 'crash_rate'),
        ]
        
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=STRATEGY_FIELDNAMES)
            writer.writeheader()
            
            for label, key in metrics_to_compare:
                for strategy_name in GA_STRATEGIES.keys():
                    convex_data = self.summary_by_strategy_path[strategy_name].get('convex', {})
                    sin_data = self.summary_by_strategy_path[strategy_name].get('sin', {})
                    
                    convex_avg = convex_data.get(key, 0)
                    convex_std = convex_data.get('std_fitness' if key == 'avg_fitness' else key.replace('avg', 'std'), 0)
                    sin_avg = sin_data.get(key, 0)
                    sin_std = sin_data.get('std_fitness' if key == 'avg_fitness' else key.replace('avg', 'std'), 0)
                    convex_min = convex_data.get('min_fitness' if key == 'avg_fitness' else key, 0)
                    convex_max = convex_data.get('max_fitness' if key == 'avg_fitness' else key, 0)
                    sin_min = sin_data.get('min_fitness' if key == 'avg_fitness' else key, 0)
                    sin_max = sin_data.get('max_fitness' if key == 'avg_fitness' else key, 0)
                    
                    diff = convex_avg - sin_avg
                    
                    if key in ['avg_fitness', 'std_fitness', 'crash_rate']:
                        convex_better = 'Yes' if convex_avg < sin_avg else 'No'
                    else:
                        convex_better = 'Yes' if convex_avg > sin_avg else 'No'
                    
                    margin = abs(diff) / max(sin_avg, 0.0001) * 100 if sin_avg != 0 else 0
                    
                    writer.writerow({
                        'metric': label,
                        'strategy': strategy_name,
                        'convex_avg': f'{convex_avg:.6f}',
                        'convex_std': f'{convex_std:.6f}',
                        'sin_avg': f'{sin_avg:.6f}',
                        'sin_std': f'{sin_std:.6f}',
                        'convex_min': f'{convex_min:.6f}',
                        'convex_max': f'{convex_max:.6f}',
                        'sin_min': f'{sin_min:.6f}',
                        'sin_max': f'{sin_max:.6f}',
                        'convex_better': convex_better,
                        'win_margin': f'{margin:.2f}%',
                    })
        
        print(f"[OK] Strategy comparison exported: {csv_path}")
    
    def _export_path_comparison(self):
        """Export path comparison across strategies"""
        csv_path = os.path.join(self.output_dir, 'benchmark_path_comparison.csv')
        
        metrics_to_compare = [
            ('Fitness (lower is better)', 'avg_fitness'),
            ('Avg Distance', 'avg_distance'),
            ('Success Rate (%)', 'success_rate'),
            ('Avg Efficiency', 'avg_efficiency'),
            ('Crash Rate (%)', 'crash_rate'),
        ]
        
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=PATH_FIELDNAMES)
            writer.writeheader()
            
            for label, key in metrics_to_compare:
                for path_name in PATHS:
                    aggressive_data = self.summary_by_strategy_path['aggressive_exploration'].get(path_name, {})
                    balanced_data = self.summary_by_strategy_path['balanced_strategy'].get(path_name, {})
                    conservative_data = self.summary_by_strategy_path['conservative_exploitation'].get(path_name, {})
                    
                    aggressive_val = aggressive_data.get(key, 0)
                    balanced_val = balanced_data.get(key, 0)
                    conservative_val = conservative_data.get(key, 0)
                    
                    aggressive_std = aggressive_data.get('std_fitness' if key == 'avg_fitness' else f'std_{key}', 0)
                    balanced_std = balanced_data.get('std_fitness' if key == 'avg_fitness' else f'std_{key}', 0)
                    conservative_std = conservative_data.get('std_fitness' if key == 'avg_fitness' else f'std_{key}', 0)
                    
                    if key in ['avg_fitness', 'crash_rate']:
                        values = [aggressive_val, balanced_val, conservative_val]
                        best_idx = values.index(min(values))
                        worst_idx = values.index(max(values))
                    else:
                        values = [aggressive_val, balanced_val, conservative_val]
                        best_idx = values.index(max(values))
                        worst_idx = values.index(min(values))
                    
                    strategy_names = ['aggressive_exploration', 'balanced_strategy', 'conservative_exploitation']
                    best_strategy = strategy_names[best_idx]
                    worst_strategy = strategy_names[worst_idx]
                    
                    writer.writerow({
                        'metric': label,
                        'path': path_name,
                        'aggressive_avg': f'{aggressive_val:.6f}',
                        'balanced_avg': f'{balanced_val:.6f}',
                        'conservative_avg': f'{conservative_val:.6f}',
                        'aggressive_std': f'{aggressive_std:.6f}',
                        'balanced_std': f'{balanced_std:.6f}',
                        'conservative_std': f'{conservative_std:.6f}',
                        'best_strategy': best_strategy,
                        'worst_strategy': worst_strategy,
                    })
        
        print(f"[OK] Path comparison exported: {csv_path}")
    
    def _export_summary_statistics(self):
        """Export summary statistics for each strategy-path combination"""
        csv_path = os.path.join(self.output_dir, 'benchmark_summary_statistics.csv')
        
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=SUMMARY_FIELDNAMES)
            writer.writeheader()
            
            for strategy_name in GA_STRATEGIES.keys():
                for path_name in PATHS:
                    data = self.summary_by_strategy_path[strategy_name].get(path_name, {})
                    
                    if data:
                        num_runs = len([r for r in self.results if r.strategy == strategy_name and r.path == path_name])
                        
                        writer.writerow({
                            'strategy': strategy_name,
                            'path': path_name,
                            'num_runs': num_runs,
                            'avg_fitness': f'{data.get("avg_fitness", 0):.6f}',
                            'std_fitness': f'{data.get("std_fitness", 0):.6f}',
                            'min_fitness': f'{data.get("min_fitness", 0):.6f}',
                            'max_fitness': f'{data.get("max_fitness", 0):.6f}',
                            'avg_distance': f'{data.get("avg_distance", 0):.2f}',
                            'avg_iterations': f'{data.get("avg_iterations", 0):.1f}',
                            'success_rate_pct': f'{data.get("success_rate", 0)*100:.1f}',
                            'avg_efficiency': f'{data.get("avg_efficiency", 0):.6f}',
                            'crash_rate_pct': f'{data.get("crash_rate", 0)*100:.1f}',
                        })
        
        print(f"[OK] Summary statistics exported: {csv_path}")
    
    def print_console_summary(self):
        """Print summary to console and save to TXT file"""
        txt_path = os.path.join(self.output_dir, 'benchmark_summary_report.txt')
        
        # Prepare summary text
        summary_lines = []
        summary_lines.append("\n" + "="*80)
        summary_lines.append("BENCHMARK SUMMARY - DETAILED ANALYSIS")
        summary_lines.append("="*80)
        
        for strategy_name in GA_STRATEGIES.keys():
            summary_lines.append(f"\n{GA_STRATEGIES[strategy_name]['name'].upper()}")
            summary_lines.append("-" * 80)
            
            for path_name in PATHS:
                data = self.summary_by_strategy_path[strategy_name].get(path_name, {})
                
                if data:
                    summary_lines.append(f"\n  {path_name.upper()} PATH:")
                    summary_lines.append(f"    Fitness:        {data.get('avg_fitness', 0):.6f} ± {data.get('std_fitness', 0):.6f}")
                    summary_lines.append(f"    Range:          [{data.get('min_fitness', 0):.6f}, {data.get('max_fitness', 0):.6f}]")
                    summary_lines.append(f"    Avg Distance:   {data.get('avg_distance', 0):.2f} px")
                    summary_lines.append(f"    Avg Iterations: {data.get('avg_iterations', 0):.1f}")
                    summary_lines.append(f"    Success Rate:   {data.get('success_rate', 0)*100:.1f}%")
                    summary_lines.append(f"    Efficiency:     {data.get('avg_efficiency', 0):.6f}")
                    summary_lines.append(f"    Crash Rate:     {data.get('crash_rate', 0)*100:.1f}%")
        
        summary_lines.append("\n" + "="*80)
        summary_lines.append("STRATEGY EFFECTIVENESS BY PATH")
        summary_lines.append("="*80)
        
        for path_name in PATHS:
            summary_lines.append(f"\n{path_name.upper()} PATH - Best Strategy:")
            best_strategy = None
            best_fitness = float('inf')
            
            for strategy_name in GA_STRATEGIES.keys():
                data = self.summary_by_strategy_path[strategy_name].get(path_name, {})
                avg_fitness = data.get('avg_fitness', float('inf'))
                
                if avg_fitness < best_fitness:
                    best_fitness = avg_fitness
                    best_strategy = strategy_name
            
            if best_strategy:
                summary_lines.append(f"  [BEST] {best_strategy.upper()}: {best_fitness:.6f}")
        
        summary_lines.append("\n" + "="*80)
        
        # Write to TXT file
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(summary_lines))
        
        # Print to console
        print('\n'.join(summary_lines))
        print(f"\n[OK] Summary report saved: {txt_path}")


if __name__ == '__main__':
    """Run comprehensive benchmark with 3 strategies on 2 paths"""    
    print("\n[*] Starting Benchmark Runner - Subprocess Approach")
    runner = BenchmarkRunner()
    runner.run_full_benchmark()
    print("\n[✓] Benchmark completed successfully!")
    print(f"[*] Results saved to: {runner.output_dir}")
