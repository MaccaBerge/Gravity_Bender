import pygame
from typing import List

NEIGHBOURING_TILES = {(-1, 1), (-1, 0), (-1, -1), (0, 1), (0, 0), (0, -1), (1, 1), (1, 0), (1, -1)}
PHYSICS_TILES = {"grass"}

class Tilemap:
    def __init__(self, game: any, tile_size: int) -> None:
        self.game = game
        self.tile_size = tile_size
        self.tile_map = {}
        self.offgrid_tiles = []

        for i in range(100):
            self.tile_map[f"{i};{5}"] = {"type": "grass", "variant": 0, "position": (i, 5)}
            self.tile_map[f"{i};{-5}"] = {"type": "grass", "variant": 0, "position": (i, -5)}
            self.tile_map[f"{0};{i}"] = {"type": "grass", "variant": 0, "position": (0, i)}
            self.tile_map[f"{20};{i}"] = {"type": "grass", "variant": 0, "position": (20, i)}
        
            self.tile_map[f"{2};{2}"] = {"type": "grass", "variant": 0, "position": (2, 2)}
    
    def get_tile_in_direction(self, position: tuple | list, direction: tuple | list, max_tile_range: int = 20) -> dict | None:
        tile_position = [int(position[0] // self.tile_size), int(position[1] // self.tile_size)]
        for _ in range(max_tile_range):
            tile_position[0] += direction[0]
            tile_position[1] += direction[1]
            tile_key = f"{tile_position[0]};{tile_position[1]}"
            if tile_key in self.tile_map:
                return self.tile_map[tile_key]

    def get_tiles_around(self, position: tuple | list) -> List[dict]:
        tile_position = (int(position[0] // self.tile_size), int(position[1] // self.tile_size))
        tiles = []
        for neighbour_tile_position in NEIGHBOURING_TILES:
            tile_key = f"{tile_position[0] + neighbour_tile_position[0]};{tile_position[1] + neighbour_tile_position[1]}"
            if tile_key in self.tile_map:
                tiles.append(self.tile_map[tile_key])
        return tiles
    
    def get_physics_rects_around(self, position: tuple | list) -> List[dict]:
        rects = []
        for tile in self.get_tiles_around(position):
            if tile["type"] in PHYSICS_TILES:
                rects.append(pygame.Rect(tile["position"][0] * self.tile_size, tile["position"][1] * self.tile_size, self.tile_size, self.tile_size))
        return rects
    
    def render(self, render_surface: pygame.Surface, offset = (0, 0)) -> None:
        for tile in self.offgrid_tiles:
            render_surface.blit(self.game.assets[tile["type"]][tile["variant"]], (tile["position"][0] - offset[0], tile["position"][1] - offset[1]))
        
        for x in range(offset[0] // self.tile_size, (offset[0] + render_surface.get_width()) // self.tile_size + 1):
            for y in range(offset[1] // self.tile_size, (offset[1] + render_surface.get_height()) // self.tile_size + 1):
                tile_key = f"{x};{y}"
                if tile_key in self.tile_map:
                    tile = self.tile_map[tile_key]
                    render_surface.blit(self.game.assets[tile["type"]][tile["variant"]], (tile["position"][0] * self.tile_size - offset[0], tile["position"][1] * self.tile_size - offset[1]))

