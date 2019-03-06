import numpy as np
import cv2
import argparse
import time
import pdb

import util

COLOR_ORDER = ['blue', 'green', 'yellow']

PRIMARY_COLORS = {
    "blue":(255, 0, 0),
    "green":(0, 255, 0),
    "yellow":(0, 0, 0)
}

COLOR_HSV = {
    "green": ((75, 5, 230), (105, 80, 255)),
    "blue": ((0, 0, 0), (0, 0, 0)),
    "yellow": ((0, 0, 0), (0, 0, 0))
}


PRIMARY_COLOR_BLUE = (255, 0, 0)
PRIMARY_COLOR_YELLOW = (0, 0, 0)

PRIMARY_COLOR_GREEN = (0, 255, 0)

FLIP_IMAGES = True

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
    cv2.namedWindow("debug", cv2.WINDOW_NORMAL)
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

        frame_points = handle_frame(frame)
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

def find_wand(img_hsv, brush_color):
    green_wand = cv2.inRange(img_hsv, COLOR_HSV[brush_color][0], COLOR_HSV[brush_color][1])
    contours, hierarchy = cv2.findContours(green_wand, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    biggest_contour = None
    for cnt in contours:
        if biggest_contour is None:
            biggest_contour = cnt
        elif cv2.contourArea(cnt) > cv2.contourArea(biggest_contour):
            biggest_contour = cnt

    if biggest_contour is not None:
        M = cv2.moments(biggest_contour)
        if M["m00"] == 0:
            return None
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])
        return (cX, cY)
    return None

def handle_frame(img):
    # Blur (remove noise)
    blurred = cv2.GaussianBlur(img, (25, 25), 0) 
    # HSV to find color
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    # Find wand top (if exists)
    points = []
    for i in range(0, 3):
        points.append(find_wand(hsv, COLOR_ORDER[i]))
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