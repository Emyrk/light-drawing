import numpy as np
import cv2
import argparse
import time
import pdb

import util

IS_CV3 = cv2.getVersionMajor() == 3

# The color order defines the player order as well.
# 'green' is the first player, yellow is the second
COLOR_ORDER = [
    #'green', 
    'yellow'
    # 'blue' <- Not really working
] 

PRIMARY_COLORS = {
    # "blue":(255, 0, 0),
    "green":(0, 255, 0),
    "yellow":(0, 255, 255)
}

COLOR_HSV = {
    "green": ((75, 30, 230), (100, 80, 255)), # TODO: Fix tolerences
    "blue": ((120, 30, 230), (150, 80, 255)),
    # From: https://stackoverflow.com/questions/9179189/detect-yellow-color-in-opencv
    "yellow": ((20, 100, 100), (30, 255, 255)) # TODO: Fix tolerences
}

# This is whether or not to mirror the image to match "right-left"
#   orientation in video. This is only used in debugging
FLIP_IMAGES = True

# p1_world_coord, p2_world_coord, p1_pixel_coord, p1_pixel_coord = VidProcessor.get_coords(frame)

# Primary function of VidProcessor
#   Params:
#       frame           Full image frame, including both wands, one, or none
#   Returns:
#       p1_world_coord  Returns the world coordinate
#       p2_world_coord
#       p1_pixel_coord  Returns coordinate for GREEN wand, if present
#       p2_pixel_coord  Returns coordinate for YELLOW wand, if present
def get_coords(frame):
    pixel_points = handle_frame(frame)
    return None, None, pixel_points[0], pixel_points[1]

# Get the player color for a given player number
def get_player_color(player_num):
    return COLOR_ORDER[player_num]

# This is for debugging
def main():
    # Argparse for filename if not default
    parser = argparse.ArgumentParser(description='Analyzing dice rolls')
    parser.add_argument("-i", help="image to anaylze", default='images/on/on-far.jpg')
    parser.add_argument("-d", action='store_true',
                        help="Turn on debugging")
    parser.add_argument("-c", action='store_true',
                        help="use camera instead of image")
    args = parser.parse_args()

    cv2.namedWindow("painted", cv2.WINDOW_NORMAL)
    cv2.namedWindow("debug-1", cv2.WINDOW_NORMAL)
    cv2.namedWindow("debug-2", cv2.WINDOW_NORMAL)
    # cv2.resizeWindow("painted", (900, 900))
    # cv2.resizeWindow("debug", (900, 900))


    if args.c == False:
        print("Using single image: %s" % args.i)
        points = handle_single_img(args.i)
        final = img = cv2.imread(args.i)
        for p in points:
            util.draw_point(final, p)
        cv2.imshow("Painted", final)
        cv2.waitKey(0)
    else:
        print("Using video camera")
        handle_webcam()

# Used for debugging to use the webcam
def handle_webcam():
    cap = cv2.VideoCapture(0)
    # 3 Wand types
    points = [[], [], []]
    last_point = [time.time(), time.time(), time.time()]
    while(True):
        # Capture frame-by-frame
        ret, frame = cap.read()
        if FLIP_IMAGES:
            frame = cv2.flip(frame, 1)

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        frame_points = handle_frame(frame, True)
        for i in range(0, len(frame_points)):
            if frame_points[i] is not None:
                if time.time() - last_point[i] > 0.5:
                    points[i].append(None)
                points[i].append(frame_points[i])
                last_point[i] = time.time()
            # Draw the lines
            util.draw_lines(frame, points[i], PRIMARY_COLORS[COLOR_ORDER[i]])

        # Display the resulting frame
        cv2.imshow('painted',frame)
        # cv2.imshow('debug', gray)
        key = cv2.waitKey(1)
        if key & 0xFF == ord('q') or key & 0xFF == 27:
            break
        if key & 0xFF == ord('c') or key & 0xFF == ord(' '):
            points = [[], [], []]


    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()

# https://solarianprogrammer.com/2015/05/08/detect-red-circles-image-using-opencv/
# https://imagecolorpicker.com/
def handle_single_img(imgsrc):
    img = cv2.imread(imgsrc)
    return handle_frame(img)

def find_wand_hsv_filter(img_hsv, brush_color, debug_image=False):
    """
    Given an hsv image and a brush color (ie: green, yellow), this method
    will find the wand head of that brush color within the image, and return the
    location of the center of the wand head

    :param img_hsv: hsv image
    :param brush_color: color of brush
    :return: location of center of brush head: (x,y) or None if not found
    """

    # Manual tolerances
    wand = cv2.inRange(img_hsv, COLOR_HSV[brush_color][0], COLOR_HSV[brush_color][1])

    if not isinstance(debug_image, bool):
        cv2.imshow('debug-2', wand)

    # the return signature is different in opencv 2 and opencv 3
    if IS_CV3:
        _, contours, hierarchy = cv2.findContours(wand, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    else:
        contours, hierarchy = cv2.findContours(wand, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)


    if not isinstance(debug_image, bool):
        circs_img = util.draw_contours(debug_image, contours)
        cv2.imshow('debug-1', circs_img)

    # get the biggest contour (this should be our wand head)
    biggest_contour = None
    for cnt in contours:
        if cv2.contourArea(cnt) < 100:
            continue
        if biggest_contour is None:
            biggest_contour = cnt
        elif cv2.contourArea(cnt) > cv2.contourArea(biggest_contour):
            biggest_contour = cnt

    # given a contour, find the center
    if biggest_contour is not None:
        M = cv2.moments(biggest_contour)
        if M["m00"] == 0:
            return None
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])
        return (cX, cY)
    return None

# Using grayscale to find the brightest points.
#   Looks for a bright circle
def find_wand_grayscale(img, brush_color):
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    ret, threshold = cv2.threshold(g, 245, 255, cv2.THRESH_BINARY)

    contours, hierarchy = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    circs = filter_circle_contours(contours)
    circs_img = util.draw_contours(img, circs)
    cv2.imshow('debug-1', circs_img)
    cv2.imshow('debug-2', threshold)



def handle_frame(img, debug=False):
    # Blur (remove noise)
    blurred = cv2.GaussianBlur(img, (25, 25), 0) 
    # HSV to find color
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    # Find wand top (if exists)
    points = []
    for i in range(0, len(COLOR_ORDER)):
        points.append(find_wand_hsv_filter(hsv, COLOR_ORDER[i], debug and img))
    # find_wand_grayscale(img, 'green')
    return points

def filter_circle_contours(contours):
    # Find the circular contours
    # http://layer0.authentise.com/detecting-circular-shapes-using-contours.html
    cricle_contour_list = []
    for contour in contours:
        approx = cv2.approxPolyDP(contour,0.01*cv2.arcLength(contour,True),True)
        area = cv2.contourArea(contour)
        if ((len(approx) > 8) & (len(approx) < 23) & (area > 30) ):
            cricle_contour_list.append(contour)
    return cricle_contour_list


def find_brushhead(primary_color):
    pass



if __name__ == "__main__":
    main()