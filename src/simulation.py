import os
import random
import time
import math
import copy
import sys
import numpy as np
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import pygame
from pygame.locals import *
from pygame.math import Vector2

import fuzzy_generator
import decoder
import vehicle
from utils import constants, path_generator
import pickle 
import argparse
import cv2
from datetime import datetime


class Simulation:
    def __init__(self, path, closed_polygon, save_video=False, polygon_name="convex"):
        pygame.init()
        pygame.display.set_caption("Trained car")
        self.screen = pygame.display.set_mode((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT), DOUBLEBUF)
        self.screen.set_alpha(False)
        self.left_screen = pygame.Surface((constants.LEFT_SCREEN_WIDTH, constants.SCREEN_HEIGHT))
        self.right_screen = pygame.Surface((constants.RIGHT_SCREEN_WIDTH, constants.SCREEN_HEIGHT))
        self.font = pygame.font.SysFont('Times New Roman', constants.FONT_SIZE)
        self.clock = pygame.time.Clock()
        self.ticks = 60
        self.exit = False
        self.car = vehicle.Car(constants.CAR_POS_X, constants.CAR_POS_Y, constants.CAR_ANGLE)

        self.path = path
        self.closed_polygon = closed_polygon
        
        # Video kaydetme
        self.save_video = save_video
        self.polygon_name = polygon_name
        self.video_writer = None
        self.frames = []
        
        if self.save_video:
            self._setup_video_output()

    def run(self, FSAngle, FSVelocity):
        car = vehicle.Car(constants.CAR_POS_X, constants.CAR_POS_Y, constants.CAR_ANGLE)

        iteration = 0
        dec = decoder.Decoder(FSAngle, FSVelocity, self.car, False)

        while not self.exit:
            dt = self.clock.get_time() / 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit = True

            ds, drot = dec.get_movement_params()
            fuzzy_text = dec.fuzzy_text
            self.car.update(dt, ds, drot)

            current_pixel_color = self.draw_screen(fuzzy_text)
            
            # Video frame kaydet
            if self.save_video:
                self._capture_frame()
            
            iteration = iteration + 1
            if self.car.is_idle(iteration) or self.car.is_collided(current_pixel_color):
                break

            self.clock.tick(self.ticks)

        # Video'yu kapat ve kaydet
        if self.save_video:
            self._finalize_video()

        pygame.quit()
        return vehicle.distance(self.car.center_position().x, self.car.center_position().y, constants.GOAL.x, constants.GOAL.y)

    def draw_screen(self, fuzzy_text):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(current_dir, constants.IMAGE_DIR, constants.IMAGE_NAME)
        car_image = pygame.image.load(image_path)
        scaled = pygame.transform.scale(car_image, (constants.CAR_WIDTH, constants.CAR_HEIGHT))

        rotated_car = pygame.transform.rotate(scaled, self.car.angle)

        self.left_screen.fill(constants.SCREEN_COLOR)
        self.draw_path(self.left_screen)

        current_pixel_value = self.left_screen.get_at((int(self.car.center_position().x), int(self.car.center_position().y)))
        self.car.left_sensor_input, self.car.front_sensor_input, self.car.right_sensor_input = self.car.get_sensors(self.left_screen)
        self.left_screen.blit(rotated_car, self.car.position)

        self.screen.blit(self.left_screen, (0, 0))
        self.right_screen.fill(constants.RIGHT_SCREEN_COLOR)
        self.screen.blit(self.right_screen, (constants.LEFT_SCREEN_WIDTH, 0))

        lines = fuzzy_text.split('\n')
        x = 0
        for line in lines:
            text = self.font.render(line, False, (0, 0, 0))
            self.screen.blit(text, (constants.LEFT_SCREEN_WIDTH, constants.FONT_SIZE*x))
            x += 1
        
        pygame.display.flip()
        
        return current_pixel_value

    def draw_path(self, screen):
        if not self.closed_polygon:
            pygame.draw.polygon(screen, constants.PATH_COLOR, self.path)
        else:
            for i, polygon in enumerate(self.path):
                if i % 2 == 0:
                    draw_color = constants.PATH_COLOR
                else:
                    draw_color = constants.SCREEN_COLOR
                pygame.draw.polygon(screen, draw_color, polygon)
    
    def _setup_video_output(self):
        """Video çıktı klasörünü hazırla"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        output_base = os.path.join(current_dir, '..', 'results', 'simulation_outputs')
        os.makedirs(output_base, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.video_filename = f"simulation_{self.polygon_name}_{timestamp}.mp4"
        self.video_path = os.path.join(output_base, self.video_filename)
        print(f"\n[*] Video kaydedilecek: {self.video_path}")
    
    def _capture_frame(self):
        """Pygame screen'den frame yakala"""
        # Screen'ı numpy array'e dönüştür
        frame_array = pygame.surfarray.array3d(self.screen)
        # Axis swap: (width, height, 3) -> (height, width, 3)
        frame_array = np.transpose(frame_array, (1, 0, 2))
        # RGB -> BGR
        frame_bgr = cv2.cvtColor(frame_array, cv2.COLOR_RGB2BGR)
        self.frames.append(frame_bgr)
    
    def _finalize_video(self):
        """Frame'leri video dosyasına kaydet"""
        if not self.frames:
            print("[!] Kaydedilecek frame yok!")
            return
        
        # Video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        fps = 30
        frame_height, frame_width, _ = self.frames[0].shape
        
        video_writer = cv2.VideoWriter(
            self.video_path, 
            fourcc, 
            fps, 
            (frame_width, frame_height)
        )
        
        # Frame'leri video'ya yaz
        for frame in self.frames:
            video_writer.write(frame)
        
        video_writer.release()
        print(f"[✓] Video kaydedildi: {self.video_path}")
        print(f"[*] Toplam frame: {len(self.frames)}")
        print(f"[*] Video süresi: {len(self.frames)/fps:.2f} saniye")

def simulate(path, is_closed, FSAngle, FSVelocity, save_video=False, polygon_name="convex"):
    os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % constants.SCREEN_POSITION
    game = Simulation(path, is_closed, save_video=save_video, polygon_name=polygon_name)
    return(game.run(FSAngle, FSVelocity))

if __name__ == '__main__':
    """
    Set up game with pretrained fuzzy system
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--polygon', choices=['convex', 'sin'], help='Runs the simulation with pretrained fuzzy system on a choosen polygon', required=True)
    parser.add_argument('--save-video', action='store_true', help='Simülasyonu video olarak kaydet')

    args = parser.parse_args()
    polygon = args.polygon
    save_video = args.save_video

    if polygon != "convex":
        path, is_closed = path_generator.generate_sin_path()
    else:
        path, is_closed = path_generator.generate_convex_polygon()
    

    with open(constants.PRETRAINED_FUZZY_PATH, 'rb') as f:
        fz = pickle.load(f)

    pygame.font.init() 
    
    FSAngle, FSVelocity = fz
    print(FSAngle)
    print(FSVelocity)

    simulate(path, is_closed, FSAngle, FSVelocity, save_video=save_video, polygon_name=polygon)