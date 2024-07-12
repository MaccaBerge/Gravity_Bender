import pygame

from animation import Animation

class Particle:
    def __init__(self, game: any, particle_type: str, particle_position: list | tuple, velocity: list | tuple = [0, 0]) -> None:
        self.game = game
        self.particle_type = particle_type
        self.particle_position = list(particle_position)
        self.velocity = list(velocity)
        self.active = False
    
    def activate(self) -> None:
        self.animation: Animation = self.game.assets[f"particle/{self.particle_type}"].copy()
        self.active = True
    
    def render(self, render_surface: pygame.Surface, offset = (0, 0)) -> None:
        image = self.animation.get_image()
        render_surface.blit(image, (self.particle_position[0] - offset[0] - image.get_width() // 2, self.particle_position[1] - offset[1] - image.get_height() // 2))

    def update(self, dt: float) -> bool:

        kill = False
        if self.animation.done:
            kill = True
            self.active = False

        self.particle_position[0] += self.velocity[0] * dt
        self.particle_position[1] += self.velocity[1] * dt

        self.animation.update()

        return kill

        