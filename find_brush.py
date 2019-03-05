import numpy as np
import cv2
import argparse
import time
import pdb

import util

PRIMARY_COLORS = {
	"blue":(255, 0, 0),
 	"green":(0, 255, 0),
 	"yellow":(0, 0, 0)
}

COLOR_HSV = {
	"green-on": (90, 30, 255)
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
    cv2.resizeWindow("painted", (900, 900))
    cv2.resizeWindow("debug", (900, 900))


    if args.c == False:
    	print("Using single image: %s" % args.i)
    	point = handle_single_img(args.i, "green")
    	final = img = cv2.imread(args.i)
    	util.draw_point(final, point)
    	cv2.imshow("Painted", final)
    	cv2.waitKey(0)
    else:
    	print("Using video camera")
    	handle_webcam()


def handle_webcam():
	cap = cv2.VideoCapture(0)
	points = []
	last_point = time.time()
	while(True):
	    # Capture frame-by-frame
	    ret, frame = cap.read()
	    if FLIP_IMAGES:
	    	frame = cv2.flip(frame, 1)

	    point = handle_frame(frame, "green")
	    if point is not None:
	    	if time.time() - last_point > 0.5:
	    		points.append(None)
	    	points.append(point)
	    	last_point = time.time()
	    # util.draw_points(frame, points)
	    util.draw_lines(frame, points)


	    # Display the resulting frame
	    cv2.imshow('painted',frame)
	    key = cv2.waitKey(1)
	    if key & 0xFF == ord('q'):
	        break
	    if key & 0xFF == ord('c'):
	        points = []


	# When everything done, release the capture
	cap.release()
	cv2.destroyAllWindows()

# https://solarianprogrammer.com/2015/05/08/detect-red-circles-image-using-opencv/
# https://imagecolorpicker.com/
def handle_single_img(imgsrc, brush_color):
	img = cv2.imread(imgsrc)
	return handle_frame(img, brush_color)

def handle_frame(img, brush_color):
	# Blur (remove noise)
	blurred = cv2.GaussianBlur(img, (25, 25), 0) 
	# HSV to find color
	hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

	# Ranges for green
	# TOOD: Allow more colors than just green
	range0 = (75, 5, 230)
	range1 = (105, 80, 255)

	# Remove all but green wand top
	r2 = cv2.inRange(hsv, range0, range1)

	# Find the contours
	contours, hierarchy = cv2.findContours(r2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

	contour_list =[]
	biggest_contour = None
	for cnt in contours:
		if biggest_contour is None:
			biggest_contour = cnt
		elif cv2.contourArea(cnt) > cv2.contourArea(biggest_contour):
			biggest_contour = cnt
	if biggest_contour is not None:
		print(cv2.contourArea(biggest_contour))
		contour_list.append(biggest_contour)


	c = util.draw_contours(img, contour_list)
	cv2.imshow("debug", c)

	if len(contour_list) == 0:
		return None
	
	M = cv2.moments(contour_list[0])
	if M["m00"] == 0:
		return None
	cX = int(M["m10"] / M["m00"])
	cY = int(M["m01"] / M["m00"])
	return (cX, cY)

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