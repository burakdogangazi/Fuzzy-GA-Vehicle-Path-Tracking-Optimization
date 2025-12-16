"""
Best vs Worst Model Comparison & Visualization
Pickle dosyalarından best ve worst modelleri yükle,
projedeki mevcut Simulation sınıfıyla çalıştır ve video olarak kaydet

Workflow:
1. train_best_worst_models.py tarafından kaydedilen pickle dosyalarını yükle
2. Projedeki Simulation sınıfıyla simüle et
3. Pygame'de yan yana göster ve mp4 video olarak kaydet

Requires: pygame, opencv-python (cv2)
pip install opencv-python

NOT: Önce train_best_worst_models.py'yi çalıştırarak modelleri eğit!
"""

import os
import sys
import csv
import pickle
import pygame
import cv2
import numpy as np
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Import project modules
import genetic_algorithm as ga
import ga_fitness
from utils import load_path as lp
from utils import constants, path_generator
import vehicle
import decoder
import fuzzy_generator
from simulation import Simulation


class BestWorstComparison:
    """Best ve Worst modelleri karşılaştır ve visualize et"""
    
    def __init__(self, benchmark_dir):
        """
        Args:
            benchmark_dir: benchmark run'ının results klasörü
                          Örn: results/benchmark/benchmark_20251127_120000/
        """
        self.benchmark_dir = benchmark_dir
        self.models_dir = os.path.join(benchmark_dir, 'models')
        self.output_dir = os.path.join(benchmark_dir, 'visualizations')
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.best_worst_models = {}  # {(strategy, path): {'best': data, 'worst': data}}
        self.load_models_from_pickle()
    
    def load_models_from_pickle(self):
        """Pickle dosyalarından best ve worst modelleri yükle"""
        print("\n" + "="*80)
        print("PICKLE DOSYALARINI YÜKLÜYORUM")
        print("="*80)
        
        if not os.path.exists(self.models_dir):
            print(f"[ERROR] Modeller klasörü bulunamadı: {self.models_dir}")
            print("[*] Lütfen önce train_best_worst_models.py'yi çalıştırın!")
            return
        
        model_files = [f for f in os.listdir(self.models_dir) if f.endswith('.pickle')]
        
        if not model_files:
            print(f"[ERROR] {self.models_dir} içinde pickle dosyası bulunamadı!")
            return
        
        print(f"\nBulunan Model Dosyaları ({len(model_files)}):")
        
        for model_file in sorted(model_files):
            filepath = os.path.join(self.models_dir, model_file)
            
            # Dosya adından bilgi çıkart: best_worst_<strategy>_<path>_<type>.pickle
            parts = model_file.replace('.pickle', '').split('_')
            if len(parts) >= 5:
                # best_worst_aggressive_exploration_convex_best.pickle
                strategy = '_'.join(parts[2:-2])  # aggressive_exploration
                path = parts[-2]  # convex
                model_type = parts[-1]  # best or worst
                
                with open(filepath, 'rb') as f:
                    fs_angle, fs_velocity = pickle.load(f)
                
                key = (strategy, path)
                if key not in self.best_worst_models:
                    self.best_worst_models[key] = {}
                
                self.best_worst_models[key][model_type] = {
                    'FSAngle': fs_angle,
                    'FSVelocity': fs_velocity,
                }
                
                print(f"  ✓ {model_file}")
        
        print(f"\n[✓] {len(self.best_worst_models)} strateji×path kombinasyonu yüklendi")
    
    def create_side_by_side_video(self, strategy, path):
        """
        Model'ı pygame'de simüle et ve video olarak kaydet
        
        Args:
            strategy: Strateji adı
            path: Yol adı
        """
        print(f"\n[*] Creating visualization for {strategy} on {path} path...")
        
        key = (strategy, path)
        
        if key not in self.best_worst_models:
            print(f"[ERROR] {strategy} + {path} için model bulunamadı")
            return
        
        model_data = self.best_worst_models[key]
        
        # Model yapısı: {'best': {...}} veya {'worst': {...}}
        if 'best' in model_data:
            model_type = 'best'
            model_info = model_data['best']
        elif 'worst' in model_data:
            model_type = 'worst'
            model_info = model_data['worst']
        else:
            print(f"[ERROR] Model yapısı hatalı: {model_data.keys()}")
            return
        
        fs_angle = model_info['FSAngle']
        fs_velocity = model_info['FSVelocity']
        
        # Yol matrisini yükle
        if path == 'convex':
            road_path, road_matrix = lp.load_convex_params()
        else:
            road_path, road_matrix = lp.load_sin_params()
        
        # Simülasyon çalıştır
        video_path = self._run_single_simulation(
            fs_angle, fs_velocity, road_matrix, strategy, path, model_type.upper()
        )
        
        print(f"[OK] Video saved: {video_path}")
    
    def _run_side_by_side_simulation(self, best_fs_angle, best_fs_velocity, 
                                      worst_fs_angle, worst_fs_velocity, 
                                      road_matrix, strategy, path):
        """
        Yan yana best vs worst simülasyon
        Pickle'dan yüklenen FSAngle ve FSVelocity'yi kullan
        """
        # Kullanılmayan metod - _run_single_simulation kullanılıyor
        pass
    
    def _run_single_simulation(self, fs_angle, fs_velocity, road_matrix, strategy, path, model_type):
        """
        Tek model simülasyonu - video'ya kaydet
        """
        # Simülasyon thread'ini çalıştır (display quitmeden)
        trajectory, crashed = self._simulate_vehicle_trajectory_from_pickle(
            fs_angle, fs_velocity, path
        )
        
        if not trajectory:
            print(f"  [ERROR] Trajectory boş!")
            return os.path.join(self.output_dir, f'{strategy}_{path}_{model_type.lower()}.mp4')
        
        # Şimdi pygame display'i kur ve video yap
        pygame.init()
        
        # Ekran boyutu
        road_width = road_matrix.shape[1]
        road_height = road_matrix.shape[0]
        padding = 20
        title_height = 40
        
        screen_width = road_width + padding * 2
        screen_height = road_height + title_height + padding
        
        screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption(f"{strategy} - {path} | {model_type}")
        clock = pygame.time.Clock()
        font_title = pygame.font.Font(None, 28)
        font_info = pygame.font.Font(None, 20)
        
        # Video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        fps = 30
        video_path = os.path.join(
            self.output_dir,
            f'{strategy}_{path}_{model_type.lower()}.mp4'
        )
        video_writer = cv2.VideoWriter(video_path, fourcc, fps, (screen_width, screen_height))
        
        print(f"  Simulating {model_type} model...")
        
        # Road surface
        road_surface = self._create_road_surface(road_matrix, model_type)
        
        max_frames = len(trajectory)
        
        # Simülasyon loop
        for frame_idx in range(max_frames):
            screen.fill((50, 50, 50))
            
            # Aracı çiz
            pos = trajectory[frame_idx]
            road_surface_copy = road_surface.copy()
            color = (0, 255, 0) if model_type == "BEST" else (255, 0, 0)
            pygame.draw.circle(road_surface_copy, color, pos, 8)
            screen.blit(road_surface_copy, (padding, title_height))
            
            # Başlık
            title = font_title.render(f"{model_type} MODEL", True, color)
            status = "CRASHED" if crashed and frame_idx >= len(trajectory) - 1 else f"Frame {frame_idx}/{max_frames}"
            info = font_info.render(f"{status} | {strategy} + {path}", True, (200, 200, 200))
            
            screen.blit(title, (padding + 10, 5))
            screen.blit(info, (padding + 10, 25))
            
            pygame.display.flip()
            clock.tick(fps)
            
            # Video'ya frame ekle
            frame_array = pygame.surfarray.array3d(screen)
            frame_array = np.transpose(frame_array, (1, 0, 2))
            frame_bgr = cv2.cvtColor(frame_array, cv2.COLOR_RGB2BGR)
            video_writer.write(frame_bgr)
        
        video_writer.release()
        pygame.quit()
        
        print(f"  [✓] Video kaydedildi: {video_path}")
        return video_path
        
        # Ekran boyutu: 2 simulation yan yana
        road_width = road_matrix.shape[1]
        road_height = road_matrix.shape[0]
        padding = 20
        title_height = 40
        
        screen_width = road_width * 2 + padding * 3
        screen_height = road_height + title_height + padding
        
        screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption(f"{strategy} - {path} | Best vs Worst")
        clock = pygame.time.Clock()
        font_title = pygame.font.Font(None, 28)
        font_info = pygame.font.Font(None, 20)
        
        # Video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        fps = 30
        video_path = os.path.join(
            self.output_dir,
            f'{strategy}_{path}_best_vs_worst.mp4'
        )
        video_writer = cv2.VideoWriter(video_path, fourcc, fps, (screen_width, screen_height))
        
        print(f"\n  Simulating...")
        print(f"  Best: Pickle'dan yüklenen model")
        print(f"  Worst: Pickle'dan yüklenen model")
        
        # Road matrisleri pygame surface'e dönüştür
        road_surface_left = self._create_road_surface(road_matrix, "BEST")
        road_surface_right = self._create_road_surface(road_matrix, "WORST")
        
        # Simulasyonlar - araçları çalıştır ve trajectory al
        best_trajectory, best_crashed = self._simulate_vehicle_trajectory_from_pickle(
            best_fs_angle, best_fs_velocity, path
        )
        worst_trajectory, worst_crashed = self._simulate_vehicle_trajectory_from_pickle(
            worst_fs_angle, worst_fs_velocity, path
        )
        
        # Fitness değerleri (bilgilendirme amaçlı)
        best_fitness = 0.0
        worst_fitness = 0.0
        
        max_frames = max(len(best_trajectory), len(worst_trajectory)) if best_trajectory and worst_trajectory else 100
        
        # Simülasyon loop
        for frame_idx in range(max_frames):
            screen.fill((50, 50, 50))
            
            # Sol: Best (yeşil)
            best_pos = None
            if best_trajectory and frame_idx < len(best_trajectory):
                best_pos = best_trajectory[frame_idx]
                road_surface_left_copy = road_surface_left.copy()
                pygame.draw.circle(road_surface_left_copy, (0, 255, 0), best_pos, 8)
                screen.blit(road_surface_left_copy, (padding, title_height))
            else:
                screen.blit(road_surface_left, (padding, title_height))
            
            # Sağ: Worst (kırmızı)
            worst_pos = None
            if frame_idx < len(worst_trajectory):
                worst_pos = worst_trajectory[frame_idx]
                road_surface_right_copy = road_surface_right.copy()
                pygame.draw.circle(road_surface_right_copy, (255, 0, 0), worst_pos, 8)
                screen.blit(road_surface_right_copy, (padding + road_width + padding, title_height))
            else:
                screen.blit(road_surface_right, (padding + road_width + padding, title_height))
            
            # Başlıklar
            best_title = font_title.render("BEST MODEL", True, (0, 255, 0))
            worst_title = font_title.render("WORST MODEL", True, (255, 0, 0))
            
            best_status = "CRASHED" if best_crashed and frame_idx >= len(best_trajectory) else "RUNNING"
            worst_status = "CRASHED" if worst_crashed and frame_idx >= len(worst_trajectory) else "RUNNING"
            
            best_info = font_info.render(
                f"Fitness: {best_fitness:.4f} | {best_status} | Frame: {min(frame_idx, len(best_trajectory))}", 
                True, (200, 200, 200)
            )
            worst_info = font_info.render(
                f"Fitness: {worst_fitness:.4f} | {worst_status} | Frame: {min(frame_idx, len(worst_trajectory))}", 
                True, (200, 200, 200)
            )
            
            screen.blit(best_title, (padding + 10, 5))
            screen.blit(worst_title, (padding + road_width + padding + 10, 5))
            screen.blit(best_info, (padding + 10, 25))
            screen.blit(worst_info, (padding + road_width + padding + 10, 25))
            
            pygame.display.flip()
            clock.tick(fps)
            
            # Video'ya frame ekle
            frame_array = pygame.surfarray.array3d(screen)
            frame_array = np.transpose(frame_array, (1, 0, 2))  # Swap axes
            frame_bgr = cv2.cvtColor(frame_array, cv2.COLOR_RGB2BGR)
            video_writer.write(frame_bgr)
        
        video_writer.release()
        pygame.quit()
        
        return video_path
    
    def _create_road_surface(self, road_matrix, label):
        """Road matrisini pygame surface'e dönüştür"""
        # Road matrisini RGB'ye dönüştür (beyaz=255 → (255,255,255))
        road_rgb = np.zeros((road_matrix.shape[0], road_matrix.shape[1], 3), dtype=np.uint8)
        
        # Beyaz (255) → Açık gri
        # Siyah (0) → Koyu gri
        road_rgb[road_matrix == 255] = [200, 200, 200]  # Açık gri = YOL
        road_rgb[road_matrix == 0] = [50, 50, 50]      # Koyu gri = DUVAR
        
        # Numpy array'ı pygame surface'e dönüştür
        surface = pygame.surfarray.make_surface(np.transpose(road_rgb, (1, 0, 2)))
        
        return surface
    
    def _simulate_vehicle_trajectory_from_pickle(self, fs_angle, fs_velocity, path_type):
        """
        Pickle'dan yüklenen FSAngle ve FSVelocity'yi kullanarak simülasyon yap
        
        Args:
            fs_angle: Pickle'dan yüklenen FSAngle
            fs_velocity: Pickle'dan yüklenen FSVelocity
            path_type: 'convex' veya 'sin'
        
        Returns:
            trajectory: [(x, y), ...] pozisyon listesi
            crashed: True eğer çarpma olmuşsa
        """
        try:
            # Path'ı yükle
            if path_type == 'convex':
                path, is_closed = path_generator.generate_convex_polygon()
            else:
                path, is_closed = path_generator.generate_sin_path()
            
            # Simülasyon çalıştır ve trajectory al
            trajectory, crashed, iterations = self._run_trajectory_capture(
                path, is_closed, fs_angle, fs_velocity
            )
            
            return trajectory, crashed
            
        except Exception as e:
            print(f"[WARNING] Simülasyon hatası: {e}")
            import traceback
            traceback.print_exc()
            return [], True
    
    def _run_trajectory_capture(self, path, is_closed, fs_angle, fs_velocity):
        """
        Simülasyon çalıştır ve aracın trajectory'sini yakala
        Pygame penceresi göstermez, sadece trajectory yakalar
        """
        os.environ['SDL_VIDEODRIVER'] = 'dummy'  # Görüntüsüz mod
        
        try:
            pygame.init()
            pygame.display.set_mode((1, 1))
            
            # Araç oluştur
            car = vehicle.Car(constants.CAR_POS_X, constants.CAR_POS_Y, constants.CAR_ANGLE)
            
            # Decoder oluştur
            dec = decoder.Decoder(fs_angle, fs_velocity, car, False)
            
            trajectory = []
            crashed = False
            iteration = 0
            max_iterations = constants.MAX_ITERATIONS if hasattr(constants, 'MAX_ITERATIONS') else 500
            
            # Sahte screen oluştur
            dummy_screen = pygame.Surface((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))
            
            # Path'ı screen'e çiz
            dummy_screen.fill(constants.SCREEN_COLOR)
            if not is_closed:
                pygame.draw.polygon(dummy_screen, constants.PATH_COLOR, path)
            else:
                for i, polygon in enumerate(path):
                    draw_color = constants.PATH_COLOR if i % 2 == 0 else constants.SCREEN_COLOR
                    pygame.draw.polygon(dummy_screen, draw_color, polygon)
            
            # Simülasyon loop
            while iteration < max_iterations:
                # Hareket parametrelerini al
                ds, drot = dec.get_movement_params()
                
                # Araç konumunu güncelle
                car.update(0.016, ds, drot)  # 60 FPS = 0.016 saniyelik frame
                
                # Pozisyonu kaydet
                car_pos = car.center_position()
                trajectory.append((int(car_pos.x), int(car_pos.y)))
                
                # Çarpışma kontrolü
                current_pixel_color = dummy_screen.get_at((int(car_pos.x), int(car_pos.y)))
                if car.is_idle(iteration) or car.is_collided(current_pixel_color):
                    crashed = True
                    break
                
                iteration += 1
            
            pygame.quit()
            return trajectory, crashed, iteration
            
        except Exception as e:
            print(f"[ERROR] Trajectory capture hatası: {e}")
            import traceback
            traceback.print_exc()
            return [], True, 0
    
    def run_all_comparisons(self):
        """Yüklenen modeller için video yap"""
        
        print("\n" + "="*80)
        print("CREATING VISUALIZATIONS")
        print("="*80)
        
        # Sadece yüklenen modelleri kullan
        for (strategy, path), model_data in self.best_worst_models.items():
            print(f"\n[*] Creating video for {strategy} + {path}")
            self.create_side_by_side_video(strategy, path)
        
        print("\n" + "="*80)
        print("ALL VISUALIZATIONS COMPLETED")
        print("="*80)


def main():
    """Main workflow"""
    
    benchmark_base = os.path.join(
        os.path.dirname(__file__), 'results', 'benchmark'
    )
    
    if not os.path.exists(benchmark_base):
        print("[ERROR] Benchmark results directory not found!")
        return
    
    # Mevcut benchmark'leri listele
    benchmark_dirs = sorted([d for d in os.listdir(benchmark_base) if d.startswith('benchmark_')])
    
    if not benchmark_dirs:
        print("[ERROR] Benchmark sonuçları bulunamadı!")
        return
    
    print("\nMevcut Benchmark Runs:")
    for i, d in enumerate(benchmark_dirs, 1):
        print(f"  {i}. {d}")
    
    # Seçim
    while True:
        try:
            choice = input(f"\nVideo üretmek istediğiniz benchmark'ı seçin (1-{len(benchmark_dirs)}): ").strip()
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(benchmark_dirs):
                selected_benchmark = benchmark_dirs[choice_idx]
                break
            else:
                print(f"Lütfen 1-{len(benchmark_dirs)} arasında bir sayı girin!")
        except ValueError:
            print("Geçersiz giriş. Lütfen bir sayı girin!")
    
    benchmark_dir = os.path.join(benchmark_base, selected_benchmark)
    print(f"\n[*] Seçilen Benchmark: {selected_benchmark}")
    
    # Comparison çalıştır
    comparison = BestWorstComparison(benchmark_dir)
    
    if not comparison.best_worst_models:
        print("[ERROR] Model yüklenmedi! Lütfen önce train_best_worst_models.py'yi çalıştırın.")
        return
    
    comparison.run_all_comparisons()
    
    print("\n[✓] Tüm video'lar başarıyla oluşturuldu!")


if __name__ == '__main__':
    main()

