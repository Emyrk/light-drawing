import cv2
import numpy as np
import Utility
import Config

NORMAL_FONT = cv2.FONT_HERSHEY_DUPLEX


def _draw_line(img, pt1, pt2, color=(255, 255, 255), stroke=1, gap=20):
    """
    Draw a dashed line between two points.
    Based on: https://stackoverflow.com/a/26711359
    :param img: OpenCV image
    :param pt1: Starting point
    :param pt2: Ending point
    :param color: RGB color of the line
    :param stroke: Stroke size of the line
    :param gap: Size of the gap between each segment
    :return: Mutated image
    """
    dist = ((pt1[0] - pt2[0]) ** 2 + (pt1[1] - pt2[1]) ** 2) ** .5
    pts = []

    for idx in np.arange(0, dist, gap):
        r = idx / dist
        x = int((pt1[0] * (1 - r) + pt2[0] * r) + .5)
        y = int((pt1[1] * (1 - r) + pt2[1] * r) + .5)
        pt = (x, y)
        pts.append(pt)

    last = pts[0]
    for idx, pt in enumerate(pts):
        if idx % 2 == 1:
            cv2.line(img, last, pt, color, stroke)
        last = pt

    return img


def _draw_text(img, text, x_pos, y_pos, size=1, color=(255, 255, 255), stroke=2):
    """
    Draws text at the specified position on the image.
    :param img: OpenCV image
    :param text: Text to draw
    :param x_pos: X position for the text
    :param y_pos: Y position for the text
    :param size: Font size multiplier
    :param color: RGB color of the text
    :param stroke: Stroke size of the text
    :return: Mutated image
    """
    if x_pos < 0 or y_pos > 1:
        raise ValueError("Invalid text position: X must be between 0 and 1")

    if y_pos < 0 or y_pos > 1:
        raise ValueError("Invalid text position: Y must be between 0 and 1")

    text_size = cv2.getTextSize(text, NORMAL_FONT, size, stroke)[0]

    # Calculate position based on image size
    text_x = int((img.shape[1] - text_size[0]) * x_pos)
    text_y = int((img.shape[0] + text_size[1]) * y_pos)

    cv2.putText(img, text, (text_x, text_y), NORMAL_FONT, size, color, stroke)

    return img


def _draw_frame(img, labels=True):
    """
    Draw the "split-screen" 2-player frame.
    :param img: OpenCV image
    :return: Mutated image
    """

    line_start = (int(img.shape[1] / 2), 0)
    line_end = (int(img.shape[1] / 2), img.shape[0])

    _draw_line(img, line_start, line_end, color=(200, 200, 200), stroke=2)

    if labels:
        _draw_text(img, "Player 1", 0.2, 0.9)
        _draw_text(img, "Player 2", 0.8, 0.9)

    return img


def _draw_cta(img, action, key="SPACE"):
    """
    Draws call-to-action text at the bottom of the image.
    :param img: OpenCV image
    :param action: Description of the action
    :param key: Key for the user to press
    :return: Mutated image
    """
    _draw_text(img, f"Press {key} to {action}", 0.5, 0.95, stroke=1)

    return img


def pre_round(frame, round):
    """
    Draws the pre-round screen.
    :param frame: OpenCV image
    :param round: Current round
    :return: Mutated image
    """
    # Header
    _draw_text(frame, "Get Ready!", 0.5, 0.2, size=3, stroke=5)
    _draw_text(frame, f"Round {round}", 0.5, 0.3)

    # Player frame
    _draw_frame(frame)

    # "Press SPACE to start"
    _draw_cta(frame, "start")

    return frame


def countdown(frame, countdown):
    """
    Draws the countdown screen.
    :param frame: OpenCV image
    :param countdown: Current countdown value
    :return: Mutated image
    """

    # Player frame
    _draw_frame(frame)

    # Countdown
    _draw_text(frame, "%.1f" % countdown, 0.5, 0.5, size=10, stroke=12)

    return frame


def playing_round(frame, ps, round, round_time, target, p1_img, p2_img):
    """
    Draws the playing screen.
    :param frame: OpenCV image
    :param ps: Playerspace details indicating the drawable area
    :param round: Current round
    :param round_time: Time left in the round
    :param target: Target image overlay
    :param p1_coords: Player 1 coordinates in pixel space
    :param p2_coords: Player 2 coordinates in pixel space
    :return: Mutated image
    """

    # Player frame
    _draw_frame(frame)

    # Round info
    _draw_text(frame, f"Round {round}", 0.99, 0.05)

    # Timer
    _draw_text(frame, "%.1f" % round_time, 0.99, 0.95)    

    # TODO: Image overlay/player coordinates
    rz = cv2.resize(target,(ps["side"],ps["side"]))
    rz = cv2.cvtColor(rz,cv2.COLOR_GRAY2BGR)

    p1space = Utility.crop_playspace(frame, ps, Config.PLAYER_ONE)
    p2space = Utility.crop_playspace(frame, ps, Config.PLAYER_TWO)

    Utility.draw_playspace(frame, ps)

    cv2.add(cv2.divide(rz, 2), p1space, p1space)
    cv2.add(cv2.divide(rz, 2), p2space, p2space)
    cv2.add(p1space, p1_img, p1space)
    cv2.add(p2space, p2_img, p2space)

    return frame


def post_round(frame, countdown, p1_score, p2_score, p1_accuracy, p2_accuracy):
    """
    Draws the end of round screen.
    :param frame: OpenCV image
    :param countdown: Time left until next round
    :param p1_score: Score for player 1
    :param p2_score: Score for player 2
    :param p1_accuracy: Percent accuracy (between 0 and 1) for player 1
    :param p2_accuracy: Percent accuracy (between 0 and 1) for player 2
    :return: Mutated image
    """

    # Player frame
    _draw_frame(frame, labels=False)

    # Timer
    _draw_text(frame, "%.1f" % countdown, 0.99, 0.95)

    # Player 1 stats
    _draw_text(frame, "Player 1", 0.15, 0.4, size=2)
    _draw_text(frame, f"Score: {p1_score}", 0.14, 0.5)
    _draw_text(frame, f"Accuracy: {p1_accuracy * 100}%", 0.15, 0.55)

    # Player 2 stats
    _draw_text(frame, "Player 2", 0.85, 0.4, size=2)
    _draw_text(frame, f"Score: {p2_score}", 0.80, 0.5)
    _draw_text(frame, f"Accuracy: {p2_accuracy * 100}%", 0.85, 0.55)

    return frame


def end_game(frame, p1_score, p2_score):
    """
    Draw the end game/scoreboard screen.
    :param frame: OpenCV image
    :param p1_score: Overall score for player 1
    :param p2_score: Overall score for player 2
    :return: Mutated image
    """
    # Header
    _draw_text(frame, "Game Over", 0.5, 0.2, size=3, stroke=5)

    # Scoreboard
    def winner(player):
        if player == 'p1' and p1_score > p2_score:
            return "*"
        elif player == 'p2' and p2_score > p1_score:
            return "*"
        return ""

    _draw_text(frame, f"{winner('p1')}Player 1: {p1_score}", 0.5, 0.4)
    _draw_text(frame, f"{winner('p2')}Player 2: {p2_score}", 0.5, 0.5)

    # "Press SPACE to play again"
    _draw_cta(frame, "play again")

    return frame


# Test Helper
if __name__ == "__main__":
    def main():
        img = np.zeros((600, 1000, 3), np.uint8)

        pre_round(img, 1)
        # countdown(img, 5)
        # playing_round(2, 32, None, None, None)
        # post_round(img, 4, 14623, 12345, 0.84, 0.95)
        # end_game(img, 14623, 12345)

        cv2.imshow('image', img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


    main()
