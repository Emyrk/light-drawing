import cv2
import numpy as np

NORMAL_FONT = cv2.FONT_HERSHEY_DUPLEX
SMALL_FONT = cv2.FONT_HERSHEY_PLAIN


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


def _draw_frame(img):
    """
    Draw the "split-screen" 2-player frame.
    :param img: OpenCV image
    :return: Mutated image
    """
    _draw_text(img, "Player 1", 0.2, 0.9)
    _draw_text(img, "Player 2", 0.8, 0.9)

    line_start = (int(img.shape[1] / 2), 0)
    line_end = (int(img.shape[1] / 2), img.shape[0])

    _draw_line(img, line_start, line_end, color=(200, 200, 200), stroke=2)

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


# Draw countdown screen
def countdown(frame, countdown):
    return frame


# Draw UI for when the round is running
# Note: target is in world space
# Note: p1 and p2 are coordinates in pixel space
def playing_round(frame, round, round_time, target, p1_coords, p2_coords):
    return frame


# Draw the end of round screen
# accuracy will be between 0 and 1
def post_round(frame, countdown, p1_score, p2_score, p1_accuracy, p2_accuracy):
    return frame


# Draw the end game screen that displays who the winner is
def end_game(frame, p1_score, p2_score):
    return frame


# Test Helper
if __name__ == "__main__":
    def main():
        img = np.zeros((600, 1000, 3), np.uint8)

        pre_round(img, 1)

        cv2.imshow('image', img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


    main()
