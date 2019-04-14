import time
import numpy as np
import cv2

# Brush size for drawing
BRUSH_SIZE = 10

def get_elapsed_time(start_time, end_time=None):
    if start_time is None:
        print("ERROR: Must have a start_time.")
        return

    if end_time is None:
        end_time = time.time()

    return end_time - start_time

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
def draw_contours(img, contours):
    contoured = img.copy()
    ci = 0
    for cnt in contours:
        alpha = 0.2
        overlay = contoured.copy()
        cv2.fillPoly(overlay, pts=[cnt], color=colors[ci%len(colors)])
        cv2.addWeighted(overlay, alpha, contoured, 1.0-alpha, 0, contoured)
        cv2.drawContours(contoured, cnt, -1, colors[ci%len(colors)], 8)
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
