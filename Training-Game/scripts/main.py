import pygame

from game import Game
from settings import Settings

class Main:
    def __init__(self) -> None:
        pygame.init()
        self.settings = Settings()
        self.screen = pygame.display.set_mode(self.settings.screen_size)

        self.game = Game(self.settings)

    def run(self) -> None:
        self.game.run()


if __name__ == "__main__":
    main = Main()
    main.run()