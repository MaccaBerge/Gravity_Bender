import pygame
import os
import time
from typing import List, Tuple

def load_image(path: str, scaling_factor: float = 1.0, size: Tuple[int, int] | None = None,  colorkey: pygame.Color | None = None) -> pygame.Surface:
    image = pygame.image.load(path).convert_alpha()

    if size:
        image = pygame.transform.scale(image, size)
    else:
        image = pygame.transform.scale_by(image, scaling_factor)

    if colorkey: 
        image.set_colorkey(colorkey)

    return image

def load_images(path: str, scaling_factor: float = 1.0, size: Tuple[int, int] | None = None, colorkey: pygame.Color | None = None) -> List[pygame.Surface]:
    images = []
    for image_name in sorted(os.listdir(path), key=lambda x: int(x.split(".")[0])):
        images.append(load_image(path + "/" + image_name, scaling_factor=scaling_factor, size=size, colorkey=colorkey))

    return images

class Timer:
    def __init__(self, duration: float | int) -> None:
        self.duration = duration
        self.is_active = False

        self.start_time = 0
        self.current_time = 0

        self.finished = False
    
    def __bool__(self) -> bool:
        return self.is_active
    
    def __eq__(self, other: bool) -> bool:
        if isinstance(other, bool):
            return self.__bool__() == other
        return NotImplemented
    
    def get_time_since_start(self) -> float:
        return self.current_time - self.start_time
    
    def start(self) -> None:
        self.start_time = int(time.time() * 1000)
        self.is_active = True
    
    def end(self) -> None:
        self.is_active = False
    
    def update(self) -> None:
        self.current_time = int(time.time() * 1000)
        self.finished = False

        if self.current_time - self.start_time >= self.duration and self.is_active:
            self.is_active = False
            self.finished = True
        
        return self.finished