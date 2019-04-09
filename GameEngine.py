import cv2
import time
import Config
import States
import UI
import Utility
from RoundGenerator import RoundGenerator
from Player import Player


class GameEngine:
    def __init__(self):
        self.state = States.IDLE
        self.prev_state = States.IDLE

        self.round = 1
        self.target = None

        self.round_start_time = time.time()
        self.countdown_start_time = time.time()
        self.post_round_start_time = time.time()

        self.p1 = Player()
        self.p2 = Player()

    def run_engine(self):
        self.state = States.PRE_ROUND

        # Grabs the window name from the config
        cv2.namedWindow(Config.WINDOW_NAME, cv2.WINDOW_NORMAL)

        cap = cv2.VideoCapture(0)
        while True:
            ret, frame = cap.read()
            if Config.FLIP_IMAGE:
                frame = cv2.flip(frame, 1)

            # Display different UIs for different game states
            if self.state == States.PRE_ROUND:
                # If this is the first loop where the state is PRE_ROUND, create a new target
                if self.state_changed():
                    self.target = RoundGenerator.get_round(self.round)

                    print("PRE_ROUND (Press Space to Continue)")

                frame = UI.pre_round(frame, self.round)

                # Wait for a player to press the space bar
                # TODO: For some reason this is not immediately responsive. Anyone can feel free to solve this problem.
                key = cv2.waitKey(1)
                if key & 0xFF == ord(' ') or key & 0xFF == 32:
                    self.state = States.COUNTDOWN

            elif self.state == States.COUNTDOWN:
                # If this is the first loop where the state is COUNTDOWN, set the start_time to the current time
                if self.state_changed():
                    print("COUNTDOWN")
                    self.countdown_start_time = time.time()

                # Get the pre round countdown time
                countdown = Config.COUNTDOWN_DURATION - Utility.get_elapsed_time(self.countdown_start_time)

                if countdown > 0:
                    frame = UI.countdown(frame, countdown)
                    print(countdown)
                else:
                    # Change the game state
                    frame = UI.countdown(frame, 0)
                    print(0)
                    self.state = States.PLAYING_ROUND

            elif self.state == States.PLAYING_ROUND:
                # If this is the first loop where the state is PLAYING_ROUND, set the start_time to the current time
                if self.state_changed():
                    print("PLAYING ROUND")
                    self.round_start_time = time.time()

                # TODO: This is where I would call VidProcessor for the list of points
                # p1_world_coord, p2_world_coord, p1_pixel_coord, p2_pixel_coord = VidProcessor.get_coords(frame)

                # Remove these once Steve implements the VidProcessor
                p1_world_coord = None
                p2_world_coord = None
                p1_pixel_coord = None
                p2_pixel_coord = None

                # Add the new drawing coordinates to each player
                self.p1.update_coord(p1_world_coord, p1_pixel_coord, self.round_start_time)
                self.p2.update_coord(p2_world_coord, p2_pixel_coord, self.round_start_time)

                # Get the current round's time
                round_time = Config.ROUND_DURATION - Utility.get_elapsed_time(self.round_start_time)

                if round_time > 0:
                    # We pass pixel coordinates because it will be quicker than to converting from world coordinates
                    frame = UI.playing_round(frame, self.round, round_time, self.target,
                                             self.p1.pixel_coords, self.p2.pixel_coords)
                else:
                    frame = UI.playing_round(frame, self.round, 0, self.target,
                                             self.p1.pixel_coords, self.p2.pixel_coords)

                    self.p1.round_over()
                    self.p2.round_over()

                    # Change the game state
                    self.state = States.POST_ROUND

            elif self.state == States.POST_ROUND:
                # If this is the first loop where the state is POST_ROUND, set the start_time to the current time
                if self.state_changed():
                    print("POST ROUND")
                    self.post_round_start_time = time.time()

                # Get the countdown to the next round/end of game
                post_round_time = Config.POST_ROUND_DURATION - Utility.get_elapsed_time(self.post_round_start_time)

                if self.p1.round_score is None:
                    # TODO: This is where we will call Josh's EvaluationEngine
                    # self.p1.round_score = EvaluationEngine.eval(self.p1.world_coords, self.target)
                    self.p1.round_score = 10
                    self.p1.round_accuracy = 0.7
                    print("P1 Score: {}".format(self.p1.round_score))
                if self.p2.round_score is None:
                    # TODO: This is where we will call Josh's EvaluationEngine
                    # self.p2.round_score = EvaluationEngine.eval(self.p2.world_coords, self.target)
                    self.p2.round_score = 8
                    self.p2.round_accuracy = 0.5
                    print("P2 Score: {}".format(self.p2.round_score))

                if post_round_time > 0:
                    frame = UI.post_round(frame, post_round_time, self.p1.round_score, self.p2.round_score,
                                          self.p1.round_accuracy, self.p2.round_accuracy)
                else:
                    # Save the current round's score to each player's total score
                    frame = UI.post_round(frame, 0, self.p1.round_score, self.p2.round_score,
                                          self.p1.round_accuracy, self.p2.round_accuracy)

                    # Saves round score
                    self.p1.save_round()
                    self.p2.save_round()

                    if self.round < Config.NUM_ROUNDS:
                        # Goes to the next round
                        self.round += 1
                        self.state = States.PRE_ROUND
                    else:
                        # Goes to the end of the game
                        self.state = States.END_GAME

            elif self.state == States.END_GAME:
                if self.state_changed():
                    print("End Game")
                    print("P1 Final Score: {}".format(self.p1.total_score))
                    print("P2 Final Score: {}".format(self.p2.total_score))
                    print("Press 'r' to play again or press 'q' to quit.")

                frame = UI.end_game(frame, self.p1.total_score, self.p2.total_score)

                key = cv2.waitKey(1)
                if key & 0xFF == ord('r') or key & 0xFF == 82:
                    self.__init__()
                    self.run_engine()

            else:
                print("ERROR: There is no state {}.".format(self.state))
                break

            cv2.imshow(Config.WINDOW_NAME, frame)
            key = cv2.waitKey(1)
            if key & 0xFF == ord('q') or key & 0xFF == 27:
                break

    def state_changed(self):
        if self.state != self.prev_state:
            self.prev_state = self.state
            return True
        return False

    def update(self):
        pass