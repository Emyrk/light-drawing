import Config
import Utility
import time


class Player:
    def __init__(self):
        self.world_coords = []
        self.is_drawing = False
        self.last_draw_time = time.time()
        self.draw_time = 0
        self.round_score = None
        self.round_accuracy = None
        self.total_score = 0

    # Add world coordinates to their respective arrays
    def update_coord(self, world_coord, round_start_time):
        time_since_last_draw = Utility.get_elapsed_time(self.last_draw_time)
        if world_coord is None and self.is_drawing and time_since_last_draw >= Config.DRAW_TIMEOUT:
            # Take the amount of time it took the player to draw their image
            self.is_drawing = False
            self.draw_time = Utility.get_elapsed_time(round_start_time)
        elif world_coord is not None:
            # If the player was not drawing before, clear their drawing coordinates
            if not self.is_drawing:
                self.clear_coords()
            self.is_drawing = True

            # Add the new point to the player's coordinates
            self.world_coords.append(world_coord)
            self.last_draw_time = time.time()

    # clear the coordinates of the player's drawing
    def clear_coords(self):
        self.world_coords = []

    # If the player is still drawing when the time runs out, max out their drawing time
    def round_over(self):
        if self.is_drawing:
            self.draw_time = Config.ROUND_DURATION
        self.is_drawing = False

    # Reset all variable except total_score
    def save_round(self):
        self.clear_coords()
        self.is_drawing = False
        self.draw_time = 0
        if self.round_score:
            self.total_score += self.round_score
        self.round_score = None
        self.round_accuracy = None

    def game_reset(self):
        self.__init__()
