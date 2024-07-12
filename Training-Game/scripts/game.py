import pygame
from sys import exit
import math
import random

from settings import Settings
from animation import Animation
from utils import load_image, load_images, Timer
from entity import Player
from tilemap import Tilemap
from particle import Particle

class Game:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.screen = pygame.display.get_surface()
        self.display = pygame.Surface(self.settings.display_size)
        self.clock = pygame.time.Clock()
        self.target_fps = self.settings.target_fps

        def create_surface(size, color) -> None:
            surf = pygame.Surface(size)
            surf.fill(color)
            return surf

        self.assets = {
            "grass": [create_surface((self.settings.tile_size, self.settings.tile_size), (0,180,0))],
            "particle/explotion": Animation(load_images(self.settings.asset_paths["particles"] + "explotion", scaling_factor=2, colorkey=(0,0,0)), image_duration=50, loop=False),
            "particle/player_switch_ground": Animation(load_images(self.settings.asset_paths["particles"] + "player_switch_ground", scaling_factor=1.5, colorkey=(0,0,0)), image_duration=50, loop=False),
            "player/idle": Animation(load_images(self.settings.asset_paths["entities"] + "player/idle", size=self.settings.entities["player"]["size"]), image_duration=150),
            "player/running": Animation(load_images(self.settings.asset_paths["entities"] + "player/running", size=self.settings.entities["player"]["size"]), image_duration=100)
        }
        
        self.movment_keys = {"left": {pygame.K_a, pygame.K_LEFT}, "right": {pygame.K_d, pygame.K_RIGHT}}

        self.player = Player(self, (50,50), self.settings.entities["player"]["size"], speed=self.settings.entities["player"]["speed"])
        self.player_movement = [False, False]

        self.tilemap = Tilemap(self, self.settings.tile_size)

        self.particles = []
        self.timed_particles = []

        self.world_offset = [0,0]

        self.particle_positions = None
    
    def spawn_particle(self, particle: Particle, delay: int = None) -> None:
        if not delay:
            particle.activate()
            self.particles.append(particle)
            return

        timer = Timer(delay)
        timer.start()

        timed_particle_data = {"particle": particle, "timer": timer}
        self.timed_particles.append(timed_particle_data)
    
    def run(self) -> None:
        while True:
            dt = self.clock.tick(self.target_fps) / 1000
            self.world_offset[0] += (self.player.get_rect().centerx - self.display.get_width() / 2 - self.world_offset[0]) * 5 * dt
            self.world_offset[1] += (self.player.get_rect().centery - self.display.get_height() / 2 - self.world_offset[1]) * 5 * dt
            render_world_offset = (int(self.world_offset[0]), int(self.world_offset[1]))
            
            self.display.fill((255,255,255))

            self.tilemap.render(self.display, offset = render_world_offset)
                
            self.player.update(dt, self.tilemap, movement = (self.player_movement[1] - self.player_movement[0], 0))
            self.player.render(self.display, offset = render_world_offset)

            if self.particle_positions:
                for position in self.particle_positions:
                    pygame.draw.circle(self.display, (255,0,0), (position[0]-self.world_offset[0], position[1]-self.world_offset[1]), 5)
            
            for timed_particle_data in self.timed_particles:
                finished = timed_particle_data["timer"].update()
                if finished: 
                    timed_particle = timed_particle_data["particle"]
                    timed_particle.activate()
                    self.particles.append(timed_particle)
                    self.timed_particles.remove(timed_particle_data)

            for particle in self.particles:
                kill = particle.update(dt)
                particle.render(self.display, self.world_offset)
                if kill:
                    self.particles.remove(particle)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key in self.movment_keys["left"]:
                        self.player_movement[0] = True
                    if event.key in self.movment_keys["right"]:
                        self.player_movement[1] = True
                    if event.key == pygame.K_SPACE:
                        self.particle_positions = self.player.switch_ground()

                if event.type == pygame.KEYUP:
                    if event.key in self.movment_keys["left"]:
                        self.player_movement[0] = False
                    if event.key in self.movment_keys["right"]:
                        self.player_movement[1] = False

            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0,0))
            pygame.display.update()
