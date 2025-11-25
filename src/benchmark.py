"""
Benchmark Script for Fuzzy Logic Vehicle Path Navigation
Compares performance between different paths (convex vs sin) with multiple GA strategies

This script:
- Uses genetic_algorithm.py's GA implementation directly
- Tests 3 different GA strategies on 2 paths
- Collects comprehensive metrics for academic evaluation
- Generates CSV reports comparing strategies and paths
- Provides statistical analysis
"""

import os
import sys
import csv
import time
import numpy as np
import copy
import random
import pickle
from datetime import datetime

# Import from genetic_algorithm.py (the actual implementation)
import genetic_algorithm as ga
import ga_fitness
import fuzzy_generator
import vehicle
import decoder
from utils import constants, load_path as lp


# ============================================================================
# BENCHMARK CONFIGURATION - 3 GA STRATEGIES
# ============================================================================

GA_STRATEGIES = {
    'aggressive': {
        'name': 'Aggressive Exploration',
        'description': 'High mutation, high diversity - explores solution space aggressively',
        'num_trainings': 3,
        'population_size': 500,
        'max_iterations': 15,
        'elitism_ratio': 0.02,
        'tournament_size': 3,
        'mutation_rate': 0.25,
        'mutation_span': 3,
        'mutation_genom_rate': 0.15,
    },
    'balanced': {
        'name': 'Balanced Strategy',
        'description': 'Moderate exploration-exploitation - steady convergence',
        'num_trainings': 3,
        'population_size': 1000,
        'max_iterations': 20,
        'elitism_ratio': 0.05,
        'tournament_size': 5,
        'mutation_rate': 0.1,
        'mutation_span': 2,
        'mutation_genom_rate': 0.1,
    },
    'conservative': {
        'name': 'Conservative Exploitation',
        'description': 'Low mutation, strong convergence - exploits known solutions',
        'num_trainings': 3,
        'population_size': 1500,
        'max_iterations': 30,
        'elitism_ratio': 0.15,
        'tournament_size': 7,
        'mutation_rate': 0.05,
        'mutation_span': 1,
        'mutation_genom_rate': 0.05,
    },
}

# ============================================================================
# METRICS COLLECTION CLASS
# ============================================================================

class BenchmarkMetrics:
    """Stores and calculates metrics for a single test run"""
    
    def __init__(self, path_name, strategy_name, training_id):
        self.path_name = path_name
        self.strategy_name = strategy_name
        self.training_id = training_id
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.fitness_value = None
        self.left_right_balance = None
        self.total_distance = None
        self.iterations_completed = None
        self.crashed = False
        self.idle = False
        self.max_iterations_reached = False
        self.collision_penalty = 0
        self.success_rate = 0
        self.efficiency_score = 0
        
    def to_dict(self):
        """Convert metrics to dictionary for CSV export"""
        return {
            'Path': self.path_name,
            'Strategy': self.strategy_name,
            'Training_ID': self.training_id,
            'Timestamp': self.timestamp,
            'Fitness_Value': round(self.fitness_value, 4) if self.fitness_value else None,
            'Left_Right_Balance': round(self.left_right_balance, 4) if self.left_right_balance else None,
            'Total_Distance': round(self.total_distance, 4) if self.total_distance else None,
            'Iterations_Completed': self.iterations_completed,
            'Crashed': int(self.crashed),
            'Idle': int(self.idle),
            'Max_Iterations_Reached': int(self.max_iterations_reached),
            'Collision_Penalty': round(self.collision_penalty, 2),
            'Success_Rate': round(self.success_rate, 4),
            'Efficiency_Score': round(self.efficiency_score, 4),
        }


# ============================================================================
# BENCHMARK RUNNER
# ============================================================================

class BenchmarkRunner:
    """Orchestrates the entire benchmark using genetic_algorithm.py"""
    
    def __init__(self):
        self.results = []
        self.summary_data = {}
        
    def run_full_benchmark(self):
        """Run complete benchmark for all paths and strategies"""
        print("\n" + "="*80)
        print("FUZZY LOGIC VEHICLE BENCHMARK - PATH & STRATEGY COMPARISON")
        print("="*80)
        print(f"\nConfiguration:")
        print(f"  - Strategies: {list(GA_STRATEGIES.keys())}")
        print(f"  - Paths: convex, sin")
        print(f"  - Total combinations: {len(GA_STRATEGIES) * 2}")
        
        paths_config = [
            ('convex', lp.load_convex_params()),
            ('sin', lp.load_sin_params()),
        ]
        
        best_solutions = {}
        
        # Train for each strategy and path combination
        for strategy_name, strategy_config in GA_STRATEGIES.items():
            print(f"\n{'#'*80}")
            print(f"# STRATEGY: {strategy_config['name'].upper()}")
            print(f"# {strategy_config['description']}")
            print(f"{'#'*80}")
            
            best_solutions[strategy_name] = {}
            
            for path_name, (path, road_matrix) in paths_config:
                print(f"\n{'*'*80}")
                print(f"* PATH: {path_name.upper()} | STRATEGY: {strategy_name.upper()}")
                print(f"{'*'*80}")
                
                best_solutions[strategy_name][path_name] = []
                
                num_trainings = strategy_config['num_trainings']
                for training_id in range(num_trainings):
                    best_chromosome = self.train_ga_for_config(
                        strategy_name, strategy_config, path_name, road_matrix, training_id + 1
                    )
                    best_solutions[strategy_name][path_name].append(best_chromosome)
        
        self.evaluate_and_compare(best_solutions, paths_config)
        self.export_results()
    
    def train_ga_for_config(self, strategy_name, config, path_name, road_matrix, training_id):
        """Train GA with specific strategy configuration"""
        print(f"\n  Training {training_id}/{config['num_trainings']} for {path_name} path...")
        
        ga.road_matrix = road_matrix
        ga.memory = {}
        ga.POPULATION_SIZE = config['population_size']
        ga.MAX_ITERATIONS = config['max_iterations']
        ga.ELITISM_RATIO = config['elitism_ratio']
        ga.TOURNAMENT_SIZE = config['tournament_size']
        ga.MUTATION_RATE = config['mutation_rate']
        ga.MUTATION_SPAN = config['mutation_span']
        ga.MUTATION_GENOM_RATE = config['mutation_genom_rate']
        
        population = ga.init_population(config['population_size'])
        
        for iteration in range(config['max_iterations']):
            population.sort()
            elites = int(population.size * config['elitism_ratio'])
            new_population = [population[i] for i in range(0, elites)]
            
            for i in range((config['population_size'] - elites) // 2):
                p1 = ga.select(population)
                p2 = ga.select(population)
                c1, c2 = ga.crossover(p1, p2)
                c1 = ga.mutate(c1)
                c2 = ga.mutate(c2)
                c1.update_fitness()
                c2.update_fitness()
                new_population.append(c1)
                new_population.append(c2)
            
            population = np.array(new_population)
            best = ga.get_best_chromosome(population)
            avg_fitness = np.mean([c.fitness for c in population])
            
            if (iteration + 1) % 5 == 0:
                print(f"    Gen {iteration+1:2d}/{config['max_iterations']}: Best={best.fitness:.4f} Avg={avg_fitness:.4f}")
        
        result = ga.get_best_chromosome(population)
        print(f"  ✓ Training {training_id} completed! Fitness: {result.fitness:.4f}")
        return result
    
    def evaluate_and_compare(self, best_solutions, paths_config):
        """Evaluate best solutions and compare paths and strategies"""
        print("\n" + "="*80)
        print("EVALUATION & COMPARISON")
        print("="*80)
        
        for strategy_name in GA_STRATEGIES.keys():
            for path_name, (path, road_matrix) in paths_config:
                print(f"\nEvaluating {strategy_name} strategy on {path_name} path...")
                
                for idx, chromosome in enumerate(best_solutions[strategy_name][path_name]):
                    fitness = chromosome.fitness
                    
                    memory = {}
                    car = vehicle.Car(constants.CAR_POS_X, constants.CAR_POS_Y, constants.CAR_ANGLE)
                    dec = decoder.Decoder(chromosome.FSAngle, chromosome.FSVelocity, car)
                    
                    iteration = 0
                    past_pos = car.center_position()
                    total_distance = 0
                    left_right_balance = 0
                    crashed = False
                    idle = False
                    collision_penalty = 0
                    
                    while iteration <= ga_fitness.MAX_ITERATIONS:
                        car.left_sensor_input, car.front_sensor_input, car.right_sensor_input = \
                            ga_fitness.get_sensors(car, road_matrix, memory)
                        ds, drot = dec.get_movement_params()
                        car.update(ga_fitness.TIME_STEP, ds, drot)
                        
                        iteration += 1
                        total_distance += ds
                        left_right_balance += abs(float(car.left_sensor_input) - float(car.right_sensor_input))
                        
                        if iteration % 100 == 0:
                            past_x, past_y = past_pos
                            curr_x, curr_y = car.center_position()
                            if vehicle.distance(past_x, past_y, curr_x, curr_y) < ga_fitness.MIN_DISTANCE:
                                break
                            else:
                                past_pos = car.center_position()
                        
                        if car.is_idle(iteration):
                            idle = True
                            collision_penalty = 50
                            break
                        
                        if car.is_collided2(road_matrix):
                            crashed = True
                            collision_penalty = 150
                            break
                    
                    metrics = BenchmarkMetrics(path_name, strategy_name, idx + 1)
                    metrics.fitness_value = fitness
                    metrics.left_right_balance = left_right_balance / max(1, iteration)
                    metrics.total_distance = total_distance
                    metrics.iterations_completed = iteration
                    metrics.crashed = crashed
                    metrics.idle = idle
                    metrics.max_iterations_reached = (iteration >= ga_fitness.MAX_ITERATIONS)
                    metrics.collision_penalty = collision_penalty
                    metrics.success_rate = 1.0 if (not crashed and not idle) else 0.0
                    metrics.efficiency_score = total_distance / (fitness + 0.0001)
                    
                    self.results.append(metrics)
                    print(f"  Training {idx+1}: Fitness={fitness:.4f} Dist={total_distance:.0f} Iter={iteration} Success={'✓' if metrics.success_rate > 0 else '✗'}")
    
    def calculate_summary(self):
        """Calculate summary statistics"""
        self.summary_data = {}
        
        for strategy_name in GA_STRATEGIES.keys():
            self.summary_data[strategy_name] = {}
            
            for path_name in ['convex', 'sin']:
                relevant_results = [m for m in self.results if m.strategy_name == strategy_name and m.path_name == path_name]
                
                if relevant_results:
                    fitness_values = [m.fitness_value for m in relevant_results]
                    distances = [m.total_distance for m in relevant_results]
                    iterations = [m.iterations_completed for m in relevant_results]
                    success_rates = [m.success_rate for m in relevant_results]
                    efficiency_scores = [m.efficiency_score for m in relevant_results]
                    
                    self.summary_data[strategy_name][path_name] = {
                        'avg_fitness': np.mean(fitness_values),
                        'std_fitness': np.std(fitness_values),
                        'min_fitness': np.min(fitness_values),
                        'max_fitness': np.max(fitness_values),
                        'avg_distance': np.mean(distances),
                        'avg_iterations': np.mean(iterations),
                        'success_rate': np.mean(success_rates),
                        'avg_efficiency': np.mean(efficiency_scores),
                    }
    
    def export_results(self):
        """Export benchmark results to CSV files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_dir = os.path.join(os.path.dirname(__file__), 'results', 'benchmark')
        os.makedirs(results_dir, exist_ok=True)
        
        self.calculate_summary()
        
        # Export detailed results
        detailed_csv = os.path.join(results_dir, f'benchmark_detailed_{timestamp}.csv')
        if self.results:
            with open(detailed_csv, 'w', newline='', encoding='utf-8') as f:
                fieldnames = list(self.results[0].to_dict().keys())
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for metric in self.results:
                    writer.writerow(metric.to_dict())
        
        print(f"\n✓ Detailed results saved to: {detailed_csv}")
        
        # Export strategy comparison
        strategy_csv = os.path.join(results_dir, f'benchmark_strategies_{timestamp}.csv')
        with open(strategy_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Metric', 'Strategy', 'Convex Path', 'Sin Path', 'Difference', 'Winner'])
            
            metrics_to_compare = [
                ('Avg Fitness (lower is better)', 'avg_fitness'),
                ('Std Fitness', 'std_fitness'),
                ('Avg Distance', 'avg_distance'),
                ('Success Rate', 'success_rate'),
                ('Efficiency Score', 'avg_efficiency'),
            ]
            
            for strategy_name in GA_STRATEGIES.keys():
                if strategy_name in self.summary_data:
                    for label, key in metrics_to_compare:
                        convex_val = self.summary_data[strategy_name].get('convex', {}).get(key, 0)
                        sin_val = self.summary_data[strategy_name].get('sin', {}).get(key, 0)
                        diff = convex_val - sin_val
                        
                        if key in ['avg_fitness', 'std_fitness']:
                            winner = 'Sin' if sin_val < convex_val else 'Convex' if convex_val < sin_val else 'Tie'
                        else:
                            winner = 'Sin' if sin_val > convex_val else 'Convex' if convex_val > sin_val else 'Tie'
                        
                        writer.writerow([label, strategy_name, f'{convex_val:.4f}', f'{sin_val:.4f}', f'{diff:.4f}', winner])
        
        print(f"✓ Strategy comparison saved to: {strategy_csv}")
        
        # Export path comparison
        path_csv = os.path.join(results_dir, f'benchmark_paths_{timestamp}.csv')
        with open(path_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Metric', 'Path', 'Aggressive', 'Balanced', 'Conservative', 'Best'])
            
            for label, key in metrics_to_compare:
                for path_name in ['convex', 'sin']:
                    aggressive_val = self.summary_data.get('aggressive', {}).get(path_name, {}).get(key, 0)
                    balanced_val = self.summary_data.get('balanced', {}).get(path_name, {}).get(key, 0)
                    conservative_val = self.summary_data.get('conservative', {}).get(path_name, {}).get(key, 0)
                    
                    if key in ['avg_fitness', 'std_fitness']:
                        values = [aggressive_val, balanced_val, conservative_val]
                        best = ['Aggressive', 'Balanced', 'Conservative'][np.argmin(values)]
                    else:
                        values = [aggressive_val, balanced_val, conservative_val]
                        best = ['Aggressive', 'Balanced', 'Conservative'][np.argmax(values)]
                    
                    writer.writerow([f'{label} ({path_name.upper()})', path_name, f'{aggressive_val:.4f}', f'{balanced_val:.4f}', f'{conservative_val:.4f}', best])
        
        print(f"✓ Path comparison saved to: {path_csv}")
        self.print_summary()
    
    def print_summary(self):
        """Print summary to console"""
        print("\n" + "="*80)
        print("BENCHMARK SUMMARY - STRATEGIES & PATHS COMPARISON")
        print("="*80)
        
        for strategy_name, strategy_config in GA_STRATEGIES.items():
            print(f"\n{strategy_name.upper()} STRATEGY - {strategy_config['name']}")
            print("-" * 80)
            
            for path_name in ['convex', 'sin']:
                if strategy_name in self.summary_data and path_name in self.summary_data[strategy_name]:
                    summary = self.summary_data[strategy_name][path_name]
                    print(f"\n  {path_name.upper()} PATH:")
                    print(f"    Avg Fitness:      {summary['avg_fitness']:.4f} ± {summary['std_fitness']:.4f}")
                    print(f"    Fitness Range:    [{summary['min_fitness']:.4f}, {summary['max_fitness']:.4f}]")
                    print(f"    Avg Distance:     {summary['avg_distance']:.2f} pixels")
                    print(f"    Success Rate:     {summary['success_rate']*100:.1f}%")
                    print(f"    Efficiency Score: {summary['avg_efficiency']:.4f}")
        
        print("\n" + "="*80)
        print("CONCLUSION: STRATEGY IMPACT ON PATH PERFORMANCE")
        print("="*80)
        
        for path_name in ['convex', 'sin']:
            print(f"\n{path_name.upper()} PATH - Best Strategy:")
            best_strategy = None
            best_fitness = float('inf')
            
            for strategy_name in GA_STRATEGIES.keys():
                if strategy_name in self.summary_data and path_name in self.summary_data[strategy_name]:
                    avg_fitness = self.summary_data[strategy_name][path_name]['avg_fitness']
                    if avg_fitness < best_fitness:
                        best_fitness = avg_fitness
                        best_strategy = strategy_name
            
            if best_strategy:
                print(f"  🏆 Winner: {best_strategy.upper()}")
                print(f"     Average Fitness: {best_fitness:.4f}")
        
        print(f"\nOVERALL - Best Path per Strategy:")
        for strategy_name in GA_STRATEGIES.keys():
            convex_fitness = self.summary_data.get(strategy_name, {}).get('convex', {}).get('avg_fitness', float('inf'))
            sin_fitness = self.summary_data.get(strategy_name, {}).get('sin', {}).get('avg_fitness', float('inf'))
            
            if convex_fitness < sin_fitness:
                winner = 'CONVEX'
                margin = ((sin_fitness - convex_fitness) / sin_fitness) * 100
            else:
                winner = 'SIN'
                margin = ((convex_fitness - sin_fitness) / convex_fitness) * 100
            
            print(f"  {strategy_name.upper()}: {winner} path ({margin:.2f}% better)")


if __name__ == '__main__':
    """Run benchmark comparing convex and sin paths with multiple GA strategies"""
    print("\n[*] Initializing Benchmark with 3 GA Strategies...")
    runner = BenchmarkRunner()
    runner.run_full_benchmark()
    print("\n[*] Benchmark completed!")
