import numpy as np
import cv2

# Colors on the resulting debug image contour borders
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
    # Add debug information for non-pruned contours
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