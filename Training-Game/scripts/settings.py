

class Settings:
    def __init__(self) -> None:
        # if i keep the display size constant, but only change the screen size, the game will look compleatley the same on any sized display. 
        self.screen_size = (2300, 1300)
        self.display_scaling_factor = 0.5
        self.display_size = (self.screen_size[0] * self.display_scaling_factor, self.screen_size[1] * self.display_scaling_factor)

        self.target_fps = 60

        self.asset_paths = {
            "graphics": "../assets/graphics/",
            "entities": "../assets/graphics/entities/",
            "particles": "../assets/graphics/particles/"
        }

        self.tile_size = 32

        self.entities = {
            "player": {"size": (11*2, 14*2), "speed": 300, "switch_ground_time": 100}
        }

        self.gravity = [0,2]#[0, 60]
        self.terminal_velocity = 1600

        
