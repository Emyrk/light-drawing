import numpy as np
import cv2
import argparse
import time
import pdb

import Utility as util
from VidProcessor import *

# https://docs.opencv.org/3.4/da/d6a/tutorial_trackbar.html

# Handles calibrating the sensitivity and thresholds
class Calibration:
    # This means we are using calibration
    def __init__(self):
        cv2.namedWindow("calibration", cv2.WINDOW_NORMAL)
        self.players = [
            PlayerCalibration("Player 1", util.COLOR_ORDER[0]),
            PlayerCalibration("Player 2", util.COLOR_ORDER[1])]
        for p in self.players:
            p.draw_tracks("calibration")

        cv2.setMouseCallback("calibration", self.calibrate)
        self.last_frame = None

        tolerance = "Tolerance"
        self.tolerance = 10
        cv2.createTrackbar(tolerance, "calibration" , 10, 100, self.on_tolerance)

    def set_hsv_range(self, player, bgr):
        pixel = np.array([[bgr]])
        hsv_pt = cv2.cvtColor(pixel, cv2.COLOR_BGR2HSV)
        util.COLOR_HSV[player.color] =  [
                        find_bound(hsv_pt[0][0], -1*self.tolerance),
                        find_bound(hsv_pt[0][0], self.tolerance)]

        print("Calibrate %s to %s" % (player.color, util.COLOR_HSV[player.color]))
        # util.COLOR_HSV[player.color] = ((65, 0, 136), (85, 13, 156))


    def on_tolerance(self, value):
        self.tolerance = value
        print("Tolerance is %d" % self.tolerance)

    def handle_frame(self, frame):
        self.last_frame = frame

        hsv = gaus_and_hsv(frame)

        # Find wand top (if exists)
        points = []
        final = [ [] for i in range(len(self.players))]

        for i in range(0, len(util.COLOR_ORDER)):
            c = util.COLOR_ORDER[i]
            pixel_map = find_pixel_range(hsv, c)
            cv2.imshow(c, pixel_map)
            contours = find_contours_hsv_filter(hsv, c)
            for c in contours:
                if cv2.contourArea(c) > 0:
                    final[i].append(c)
    
        cnt = frame
        for i in range(len(final)):
            cnt = util.draw_contours(cnt, final[i], (255, 255, 255), 1)
        cv2.imshow("calibration", cnt)

    def calibrate(self, event, x, y, flags, param):
        # if the left mouse button was clicked
        if event == cv2.EVENT_LBUTTONDOWN:
            print(self.last_frame[y][x])
            self.set_hsv_range(self.players[0], self.last_frame[y][x])
            pass

        elif event == cv2.EVENT_RBUTTONDOWN:
            pass



class PlayerCalibration:
    def __init__(self, name, color):
        self.name = name
        self.color = color

    def draw_tracks(self, win):
        return
        hue_trackbar = "%s Hue Channel" % self.name
        cv2.createTrackbar(hue_trackbar, "calibration" , 0, 180, self.on_hue)
        sat_trackbar = "%s Sat Channel" % self.name
        cv2.createTrackbar(sat_trackbar, "calibration" , 0, 255, self.on_sat)
        val_trackbar = "%s Val Channel" % self.name
        cv2.createTrackbar(val_trackbar, "calibration" , 0, 255, self.on_val)

    def on_hue(self, val):
        print("Hue is %d" % val)
    def on_val(self, val):
        print("Val is %d" % val)
    def on_sat(self, val):
        print("Sat is %d" % val)


def find_bound(hsv, tolerance):
    return (int(max(hsv[0] + tolerance, 0)),
            int(max(hsv[1] +tolerance, 0)),
            int(max(hsv[2] +tolerance, 0)))

# This is for debugging
def main():
    # Argparse for filename if not default
    parser = argparse.ArgumentParser(description='Analyzing dice rolls')
    parser.add_argument("-i", help="image to anaylze", default='images/on/on-far.jpg')
    parser.add_argument("-d", action='store_true',
                        help="Turn on debugging")
    parser.add_argument("-c", action='store_true',
                        help="use camera instead of image")
    parser.add_argument('-v', metavar='VIDEO_CAME', type=int,
                        help='Choose video camera', default=0)
    args = parser.parse_args()

    # cv2.namedWindow("painted", cv2.WINDOW_NORMAL)
    # cv2.namedWindow("debug-1", cv2.WINDOW_NORMAL)
    # cv2.namedWindow("debug-2", cv2.WINDOW_NORMAL)
    # cv2.namedWindow("playspace", cv2.WINDOW_NORMAL)
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
        handle_webcam(args.v)

# Used for debugging to use the webcam
def handle_webcam(cam):
    cali = Calibration()
    cap = cv2.VideoCapture(cam)
    # uvcdynctrl -f
    # cap.set(3,800) # Width
    # cap.set(4,600) # Height
    # 3 Wand types
    points = [[], [], []]
    last_point = [time.time(), time.time(), time.time()]
    while(True):
        # Capture frame-by-frame
        ret, frame = cap.read()
        cali.handle_frame(frame)

        # cv2.imshow('debug', gray)
        key = cv2.waitKey(1)
        if key & 0xFF == ord('q') or key & 0xFF == 27:
            break
        if key & 0xFF == ord('c') or key & 0xFF == ord(' '):
            points = [[], [], []]


    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()