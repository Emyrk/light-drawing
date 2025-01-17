import cv2
import time
import Config
import States
import UI
import Utility
from RoundGenerator import RoundGenerator
from DrawingEngine import DrawingEngine
from EvaluationEngine import EvaluationEngine
from Player import Player
from DebugUtils import display_all_img
import VidProcessor

class GameEngine:
    def __init__(self, camera):
        self.camera = camera
        self.state = States.IDLE
        self.prev_state = States.IDLE

        self.round = 1
        self.target = None
        self.round_max_time = 0

        self.round_start_time = time.time()
        self.countdown_start_time = time.time()
        self.post_round_start_time = time.time()

        self.p1 = Player()
        self.p2 = Player()

        self.evaluation_engine = EvaluationEngine(0.7)

    def run_engine(self):
        self.state = States.PRE_ROUND

        # Grabs the window name from the config
        cv2.namedWindow(Config.WINDOW_NAME, cv2.WINDOW_NORMAL)

        cap = cv2.VideoCapture(self.camera)
        # uvcdynctrl -f
        res = [(800, 600), (1280, 720)]
        chosen = res[0]
        cap.set(3, chosen[0])  # Width
        cap.set(4, chosen[1])  # Height
        while True:
            ret, frame = cap.read()
            if Config.FLIP_IMAGE:
                frame = cv2.flip(frame, 1)

            # Display different UIs for different game states
            if self.state == States.PRE_ROUND:
                # If this is the first loop where the state is PRE_ROUND, create a new target
                if self.state_changed():
                    round = RoundGenerator.get_round(self.round)
                    self.target = round[0]
                    self.round_max_time = round[1]

                    print("PRE_ROUND (Press Space to Continue)")

                frame = UI.pre_round(frame, self.round)

                # Wait for a player to press the space bar
                # TODO: For some reason this is not immediately responsive. Anyone can feel free to solve this problem.
                key = cv2.waitKey(1)
                if key == ord(' ') or key == 32:
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

                # Get the playable space such that each sub component knows the player's draw space
                ps = Utility.playable_space(frame)

                # TODO: This is where I would call VidProcessor for the list of points
                p1_world_coord = VidProcessor.get_coords(frame, ps, Config.PLAYER_ONE) # Player 1
                p2_world_coord = VidProcessor.get_coords(frame, ps, Config.PLAYER_TWO) # Player 2

                # Add the new drawing coordinates to each player
                self.p1.update_coord(p1_world_coord, self.round_start_time)
                self.p2.update_coord(p2_world_coord, self.round_start_time)

                # Get the current round's time
                round_time = self.round_max_time - Utility.get_elapsed_time(self.round_start_time)

                p1_drawing = DrawingEngine.draw(self.p1.world_coords, ps.get("side"), ps.get("side"),
                                                Utility.PRIMARY_COLORS[Utility.COLOR_ORDER[Config.PLAYER_ONE]])
                p2_drawing = DrawingEngine.draw(self.p2.world_coords, ps.get("side"), ps.get("side"),
                                                Utility.PRIMARY_COLORS[Utility.COLOR_ORDER[Config.PLAYER_TWO]])

                print("p1 points: {}".format(len(self.p1.world_coords)))


                if round_time > 0:
                    # We pass pixel coordinates because it will be quicker than to converting from world coordinates
                    frame = UI.playing_round(frame, ps, self.round, round_time, self.target,
                                             p1_drawing, p2_drawing)
                else:
                    frame = UI.playing_round(frame, ps, self.round, 0, self.target,
                                             p1_drawing, p2_drawing)

                    self.p1.round_over()
                    self.p2.round_over()

                    # Change the game state
                    self.state = States.POST_ROUND

            elif self.state == States.POST_ROUND:
                # If this is the first loop where the state is POST_ROUND, set the start_time to the current time
                print("p1 draw time: {}".format(self.p1.draw_time))
                print("p2 draw time: {}".format(self.p2.draw_time))
                if self.state_changed():
                    print("POST ROUND")
                    self.post_round_start_time = time.time()

                # Get the countdown to the next round/end of game
                post_round_time = Config.POST_ROUND_DURATION - Utility.get_elapsed_time(self.post_round_start_time)

                # Get the playable space such that each sub component knows the player's draw space
                ps = Utility.playable_space(frame)

                p1_drawing = DrawingEngine.draw(self.p1.world_coords, ps.get("side"), ps.get("side"),
                                Utility.PRIMARY_COLORS[Utility.COLOR_ORDER[Config.PLAYER_ONE]])
                p2_drawing = DrawingEngine.draw(self.p2.world_coords, ps.get("side"), ps.get("side"),
                                                Utility.PRIMARY_COLORS[Utility.COLOR_ORDER[Config.PLAYER_TWO]])

                p1_drawing_binary = cv2.cvtColor(p1_drawing, cv2.COLOR_BGR2GRAY)
                p2_drawing_binary = cv2.cvtColor(p2_drawing, cv2.COLOR_BGR2GRAY)
                p1_drawing_binary = cv2.threshold(p1_drawing_binary, 30, 255, cv2.THRESH_BINARY)[1]
                p2_drawing_binary = cv2.threshold(p2_drawing_binary, 30, 255, cv2.THRESH_BINARY)[1]

                if self.p1.round_score is None:
                    # TODO: convert p1 world coordinates to world size image before passing to evaluate
                    evaluation = self.evaluation_engine.evaluate(self.target, p1_drawing_binary, self.round_max_time, self.p1.draw_time)
                    self.p1.round_score = evaluation[1]
                    self.p1.round_accuracy = evaluation[0]
                    print("P1 Score: {}".format(self.p1.round_score))
                if self.p2.round_score is None:
                    # TODO: convert p2 world coordinates to world size image before passing to evaluate
                    evaluation = self.evaluation_engine.evaluate(self.target, p2_drawing_binary, self.round_max_time, self.p2.draw_time)
                    self.p2.round_score = evaluation[1]
                    self.p2.round_accuracy = evaluation[0]
                    print("P2 Score: {}".format(self.p2.round_score))

                if post_round_time > 0:
                    frame = UI.post_round(frame, post_round_time, self.p1.round_score, self.p2.round_score,
                                          self.p1.round_accuracy, self.p2.round_accuracy, ps, self.target, p1_drawing, p2_drawing)
                else:
                    # Save the current round's score to each player's total score
                    frame = UI.post_round(frame, 0, self.p1.round_score, self.p2.round_score,
                                          self.p1.round_accuracy, self.p2.round_accuracy, ps, self.target, p1_drawing, p2_drawing)

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
                if key == ord('r') or key == 82:
                    cap.release()
                    self.__init__(self.camera)
                    self.run_engine()

            else:
                print("ERROR: There is no state {}.".format(self.state))
                break

            cv2.imshow(Config.WINDOW_NAME, frame)
            key = cv2.waitKey(1)
            if key == ord('q') or key == 27:
                break

    def state_changed(self):
        if self.state != self.prev_state:
            self.prev_state = self.state
            return True
        return False
