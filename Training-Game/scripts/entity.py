import pygame
import time
import math 
import random

from tilemap import Tilemap
from animation import Animation
from utils import Timer
from particle import Particle
from utils import Timer

class Physics_Entity:
    def __init__(self, game: any, entity_type: str, position: tuple | list, size: tuple | list, speed: int = 600, graivty: list | tuple = [0, 60]) -> None:
        self.game = game
        self.entity_type = entity_type
        self.position = list(position)
        self.size = size
        self.speed = speed
        self.velocity = [0, 0]
        self.gravity = list(graivty)
        self.collisions = {"top": False, "bottom": False, "left": False, "right": False}

        self.action = ""
        self.flip = [False, False]
        self.animation_offset = [0,0]
        self.ground_selected = True
        self.switch_ground_data = {"is_switching": False, "switch_time_ms": self.game.settings.entities[self.entity_type]["switch_ground_time"], 
                                   "time_between_particle_spawn_ms": None, "end_position": None, "particle_type": f"{self.entity_type}_switch_ground", 
                                   "particle_separation": 20, "movement_dy": None}
        self.set_action("idle")
    
    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(self.position[0], self.position[1], self.size[0], self.size[1])
    
    def get_hitbox_rects(self, frame_movement: list | tuple) -> dict:
        frame_movement = list(frame_movement)
        rect = self.get_rect()
        hitboxes = {"horizontal": None, "vertical": None}

        hitboxes["horizontal"] = rect
        hitboxes["vertical"] = pygame.Rect(rect.left, rect.top, rect.width, rect.height+4) if (frame_movement[1] > 0) else pygame.Rect(rect.left, rect.top-4, rect.width, rect.height)
    
        return hitboxes
    
    def set_action(self, action: str) -> None:
        if action != self.action:
            self.action = action
            self.animation: Animation = self.game.assets[f"{self.entity_type}/{self.action}"].copy()
    
    def switch_ground(self) -> None:
        if self.switch_ground_data["is_switching"]: return

        rect = self.get_rect()
        direction = (0, -1 if self.ground_selected else 1)
        tile_size = self.game.tilemap.tile_size
        number_of_rays = max(int(rect.width // self.game.tilemap.tile_size), 2)
        distance_between_rays = rect.width / (number_of_rays - 1)

        tiles = []
        for i in range(number_of_rays):
            tile = self.game.tilemap.get_tile_in_direction( (int(rect.midleft[0] + distance_between_rays * i - (1 if i == number_of_rays - 1 else 0)), rect.centery), direction)
            if tile: tiles.append(tile)
        
        if not tiles: return

        target_tile = min(tiles, key = lambda x: abs((x["position"][1] * tile_size) - rect.centery))

        if not target_tile: return

        self.switch_ground_data["is_switching"] = True
        self.switch_ground_data["timer"] = Timer(self.switch_ground_data["switch_time_ms"])

        self.ground_selected = not self.ground_selected
        self.gravity[1] *= -1
        
        tile_y_position_pixels = target_tile["position"][1] * tile_size
        
        if self.ground_selected:
            end_position = (int(self.position[0]), tile_y_position_pixels)
        else:
            end_position = (int(self.position[0]), tile_y_position_pixels + tile_size)
        
        self.switch_ground_data["end_position"] = end_position

        self.switch_ground_data["movement_dy"] = (self.switch_ground_data["end_position"][1] - self.position[1]) / self.switch_ground_data["switch_time_ms"]
        number_of_particles = int(abs(self.switch_ground_data["end_position"][1] - rect.centery) // self.switch_ground_data["particle_separation"]) + 1# can affect where the last particle spawns
        self.switch_ground_data["time_between_particle_spawn_ms"] = int(self.switch_ground_data["switch_time_ms"] / number_of_particles)

        start_position = rect.center
        for i in range(number_of_particles):
            position = (start_position[0], start_position[1] + (i * self.switch_ground_data["particle_separation"] * (1 if self.ground_selected else -1)))
            particle_velocity = (0, (1 if self.ground_selected else -1) * random.random() * 300)
            self.game.spawn_particle(Particle(self.game, self.switch_ground_data["particle_type"], position, velocity=particle_velocity), delay=self.switch_ground_data["time_between_particle_spawn_ms"]*i)
        
    
    def render(self, render_surface: pygame.Surface, offset = (0,0)) -> None:
        if not self.switch_ground_data["is_switching"]:
            render_surface.blit(pygame.transform.flip(self.animation.get_image(), not self.flip[0], self.flip[1]), (self.position[0] - offset[0] + self.animation_offset[0], self.position[1] - offset[1] + self.animation_offset[1]))

        # hitboxes = self.get_hitbox_rects(self.frame_movement)
        # verticle_hitbox = hitboxes["vertical"]
        # horizontal_hitbox = hitboxes["horizontal"]
        # pygame.draw.rect(render_surface, (255, 0, 0), pygame.Rect(verticle_hitbox.left - offset[0], verticle_hitbox.top - offset[1], verticle_hitbox.width, verticle_hitbox.height))
        # pygame.draw.rect(render_surface, (0,255, 0), pygame.Rect(horizontal_hitbox.left - offset[0], horizontal_hitbox.top - offset[1], horizontal_hitbox.width, horizontal_hitbox.height))

    def update(self, dt: float, tilemap: Tilemap, movement = (0,0)) -> None:
        self.collisions = {"top": False, "bottom": False, "left": False, "right": False}

        frame_movement = (((movement[0] * self.speed) + self.velocity[0]) * dt, ((movement[1] * self.speed) + self.velocity[1] * dt))
        self.frame_movement = frame_movement

        if self.switch_ground_data["is_switching"]: 
            frame_movement = (0, 0)
            self.velocity[1] = 0
        
        self.position[0] += frame_movement[0]
        entity_rect = self.get_rect()
        entity_hitboxes = self.get_hitbox_rects(frame_movement)
        for rect in tilemap.get_physics_rects_around(entity_rect.center):
            if entity_hitboxes["horizontal"].colliderect(rect):
                if frame_movement[0] > 0:
                    entity_rect.right = rect.left
                    self.collisions["right"] = True
                if frame_movement[0] < 0:
                    entity_rect.left = rect.right
                    self.collisions["left"] = True
                self.position[0] = entity_rect.x
        
        self.position[1] += frame_movement[1]
        entity_rect = self.get_rect()
        entity_hitboxes = self.get_hitbox_rects(frame_movement)
        for rect in tilemap.get_physics_rects_around(entity_rect.center):
            if entity_hitboxes["vertical"].colliderect(rect):
                if frame_movement[1] > 0:
                    entity_rect.bottom = rect.top
                    self.collisions["bottom"] = True
                if frame_movement[1] < 0:
                    entity_rect.top = rect.bottom
                    self.collisions["top"] = True
                self.position[1] = entity_rect.y
        
        if self.collisions["top"] or self.collisions["bottom"]:
            self.velocity[1] = 0
        
        if movement[0] > 0:
            self.flip[0] = False
        if movement[0] < 0:
            self.flip[0] = True
        
        self.flip[1] = False if self.gravity[1] > 0 else True

        self.velocity[1] = min(max(self.velocity[1] + self.gravity[1], -self.game.settings.terminal_velocity), self.game.settings.terminal_velocity)

        if self.switch_ground_data["is_switching"]:
            timer = self.switch_ground_data["timer"]
            if not timer:
                timer.start()
                for i in range(20):
                    angle = random.random() * math.pi * 2
                    speed = random.random() * 50 + 50
                    particle_velocity = [math.cos(angle) * speed, math.sin(angle) * speed]
                    self.game.spawn_particle(Particle(self.game, self.switch_ground_data["particle_type"], self.get_rect().center, velocity=particle_velocity))

            finished = timer.update()

            if finished:
                self.switch_ground_data["is_switching"] = False
                rect = self.get_rect()
                end_position = self.switch_ground_data["end_position"]
                if self.ground_selected:
                    rect.bottom = end_position[1]
                else:
                    rect.top = end_position[1]
                self.position[1] = rect.y
                for i in range(20):
                    angle = random.random() * math.pi * 2
                    speed = random.random() * 50 + 50
                    particle_velocity = [math.cos(angle) * speed, math.sin(angle) * speed]
                    self.game.spawn_particle(Particle(self.game, self.switch_ground_data["particle_type"], self.get_rect().center, velocity=particle_velocity))
            else:
                self.position[1] += self.switch_ground_data["movement_dy"] * (dt*1000)
            
        self.animation.update()



class Player(Physics_Entity):
    def __init__(self, game: any, position: list | tuple, size: list | tuple, speed: float | int = 800) -> None:
        super().__init__(game, "player", position, size, speed=speed)
    
    def update(self, dt: float, tilemap: Tilemap, movement: list | tuple = (0, 0)) -> None:
        super().update(dt, tilemap, movement=movement)

        if movement[0] != 0:
            self.set_action("running")
        else:
            self.set_action("idle")

        

  