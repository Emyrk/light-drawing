import os
import sys
import time
import numpy as np
import cv2
from Config import *

# Brush size for drawing
BRUSH_SIZE = 10

# Horizontal buffer for playspaces
PLAYSPACE_BUFFER = 10

# The color order defines the player order as well.
# 'green' is the first player, yellow is the second
COLOR_ORDER = [
    'yellow',
    'green' 
    # 'blue' # <- Not really working
]

PRIMARY_COLORS = {
    "blue":(255, 0, 0),
    "green":(0, 255, 0),
    "yellow":(0, 255, 255)
}

COLOR_HSV = {
    "green": [(70, 28, 235), (110, 68, 275)],#[(48, 81, 242), (68, 101, 262)], # TODO: Fix tolerences
    "blue": [(75, 153, 235), (115, 193, 275)],#[(80, 233, 233), (120, 273, 273)],
    # From: https://stackoverflow.com/questions/9179189/detect-yellow-color-in-opencv
    "yellow": [(155, 0, 245), (175, 12, 265)]#[(10, 90, 235), (50, 130, 275)]
 # TODO: Fix tolerences
}

def get_elapsed_time(start_time, end_time=None):
    if start_time is None:
        print("ERROR: Must have a start_time.")
        return

    if end_time is None:
        end_time = time.time()

    return end_time - start_time


# Will return the upper left, lower right of the two playable
#   spaces.
# +-------------+
# |      |      |
# |ltl   |rtl   |
# |      |      |
# |   lbr|   rbr|
# |      |      |
# +-------------+
#       midx
def playable_space(frame):
    width = int(frame.shape[1])
    height = int(frame.shape[0])
    side = int(width/2) - PLAYSPACE_BUFFER

    # vertical & horizontal offset
    vOffset = (height-side)/2
    hOffset = (width-side*2)/4
    midx = int(width/2)

    return {"ltl":(int(hOffset), int(vOffset)), "lbr":(int(midx-hOffset), int(height-vOffset)),
            "rtl":(int(midx+hOffset), int(vOffset)), "rbr":(int(width-hOffset), int(height-vOffset)),
            "side":side}

# draw_playspace will draw the playspace on the frame passed in.
#   It does not draw on a copy
def draw_playspace(frame, playspace):
    overlay = frame.copy()

    cv2.rectangle(overlay, playspace["ltl"], playspace["lbr"],
        (255, 255, 255), -1)
    alpha = 0.1
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha,
        0, frame)

    cv2.rectangle(overlay, playspace["rtl"], playspace["rbr"],
        (255, 255, 255), -1)
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha,
        0, frame)
    return frame

# crop_playspace will crop out the playspace from the flame to player 0 and player 1 space
def crop_playspace(frame, playspace, player):
    # Crop frame space to playerspace
    # crop_img = img[y:y+h, x:x+w]
    if player == PLAYER_ONE:
        return frame[playspace["ltl"][1]:playspace["lbr"][1], playspace["ltl"][0]:playspace["lbr"][0]]
    else:
        return frame[playspace["rtl"][1]:playspace["rbr"][1], playspace["rtl"][0]:playspace["rbr"][0]]

# Colors on the resulting debug image contour borders
#   Contours will be drawn with different colors
colors = [
    (255, 0, 0),
    # (0, 255, 0),
    (0, 0, 255),
    (255, 255, 0),
    (255, 0, 255),
    (0, 255, 255),
]

# Draws contours and fills in the area on an image.
def draw_contours(img, contours, color=None, alpha=0.5):
    contoured = img.copy()
    ci = 0
    for cnt in contours:
        overlay = contoured.copy()
        c = color or colors[ci%len(colors)]
        cv2.fillPoly(overlay, pts=[cnt], color=c)
        cv2.addWeighted(overlay, alpha, contoured, 1.0-alpha, 0, contoured)
        cv2.drawContours(contoured, cnt, -1, c, 8)
        ci += 1
    return contoured

# https://stackoverflow.com/questions/10469235/opencv-apply-mask-to-a-color-image
def mask_colored(img, mask):
    fg = cv2.bitwise_or(img, img, mask=mask)
    mask = cv2.bitwise_not(mask)
    background = np.full(img.shape, 255, dtype=np.uint8)
    bk = cv2.bitwise_or(background, background, mask=mask)
    final = cv2.bitwise_or(fg, bk)
    return final

# Does not make a copy
def draw_point(img, point):
    cv2.circle(img, point, BRUSH_SIZE, (0, 255, 0), -1)

def draw_points(img, points):
    for p in points:
        draw_point(img, p)

def draw_line(img, p1, p2, color):
    cv2.line(img, p1, p2, color, thickness=3, lineType=8)

def draw_lines(img, points, color):
    if len(points) == 0:
        return
    for i in range(1, len(points)):
        if points[i -1] is None or points[i] is None:
            continue
        draw_line(img, points[i-1], points[i], color)


class HideOutput:
    """
    A context manager for doing a "deep suppression" of stdout and stderr in
    Python, i.e. will suppress all print, even if the print originates in a
    compiled C/Fortran sub-function.

    This will not suppress raised exceptions, since exceptions are printed
    to stderr just before a script exits, and after the context manager has
    exited.

    Source: https://stackoverflow.com/q/11130156
    """

    def __init__(self):
        # Open a pair of null files
        self.null_fds = [os.open(os.devnull, os.O_RDWR) for _ in range(2)]

        # Save the actual stdout (1) and stderr (2) file descriptors.
        self.save_fds = [os.dup(1), os.dup(2)]

    def __enter__(self):
        # Assign the null pointers to stdout and stderr.
        os.dup2(self.null_fds[0], 1)
        os.dup2(self.null_fds[1], 2)

    def __exit__(self, *_):
        # Re-assign the real stdout/stderr back to (1) and (2)
        os.dup2(self.save_fds[0], 1)
        os.dup2(self.save_fds[1], 2)

        # Close all file descriptors
        for fd in self.null_fds + self.save_fds:
            os.close(fd)
