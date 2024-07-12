import pygame
from typing import Union
import time

class Animation():
    def __init__(self, images: list, image_duration: Union[float, int] = 100, loop: bool = True) -> None:
        self.images = images
        self.image_duration = image_duration
        self.loop = loop
        self.done = False

        self.image = 0
        self.number_of_images = len(images)

        self.start_time_s = time.time()
        self.current_time_s = self.start_time_s
        self.time_elapsed_ms = 0
    
    def _calculate_image(self) -> int:
        if self.loop:
            return int(self.time_elapsed_ms // self.image_duration) % self.number_of_images
        else:
            return min(int(self.time_elapsed_ms // self.image_duration), self.number_of_images)  
    
    def copy(self) -> "Animation":
        return Animation(images = self.images, image_duration = self.image_duration, loop = self.loop)
    
    def get_image(self) -> pygame.Surface:
        return self.images[self.image]

    def update(self) -> None:
        self.current_time_s = time.time()
        self.time_elapsed_ms = int((self.current_time_s - self.start_time_s)*1000)

        self.image = self._calculate_image()
        
        if self.image > self.number_of_images - 1:
            self.image = self.number_of_images - 1
            self.done = True

    

