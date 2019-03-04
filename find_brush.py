import numpy as np
import cv2
import argparse
import pdb

import util

BRUSH_SIZE = 20

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

def main():
    # Argparse for filename if not default
    parser = argparse.ArgumentParser(description='Analyzing dice rolls')
    parser.add_argument("-i", help="image to anaylze", default='images/on/on-far.jpg')
    parser.add_argument("-d", action='store_true',
                        help="Turn on debugging")
    parser.add_argument("-c", action='store_true',
                        help="use camera instead of image")
    args = parser.parse_args()

    cv2.namedWindow("Painted")

    if args.c == False:
    	print("Using single image: %s" % args.i)
    	final = handle_single_img(args.i, "green")
    	cv2.imshow("Painted", final)
    	cv2.waitKey(0)
    else:
    	print("Using video camera")


# https://solarianprogrammer.com/2015/05/08/detect-red-circles-image-using-opencv/
# https://imagecolorpicker.com/
def handle_single_img(imgsrc, brush_color):
	img = cv2.imread(imgsrc)
	# Blur (remove noise)
	blurred = cv2.GaussianBlur(img, (25, 25), 0) 
	# HSV to find color
	hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

	# Ranges for green
	# TOOD: Allow more colors than just green
	range0 = (80, 5, 230)
	range1 = (100, 80, 255)

	# Remove all but green wand top
	r2 = cv2.inRange(hsv, range0, range1)

	# Find the contours
	contours, hierarchy = cv2.findContours(r2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

	# Find the circular contours
	# http://layer0.authentise.com/detecting-circular-shapes-using-contours.html
	contour_list = []
	for contour in contours:
	    approx = cv2.approxPolyDP(contour,0.01*cv2.arcLength(contour,True),True)
	    area = cv2.contourArea(contour)
	    if ((len(approx) > 8) & (len(approx) < 23) & (area > 30) ):
	        contour_list.append(contour)

	# draw the brush stroke
	final = img.copy()
	for cnt in contour_list:
		M = cv2.moments(cnt)
		cX = int(M["m10"] / M["m00"])
		cY = int(M["m01"] / M["m00"])
		cv2.circle(final, (cX, cY), BRUSH_SIZE, (0, 255, 0), -1)


	# c = util.draw_contours(img, contour_list)
	# cv2.imshow("Final", final)
	# TODO: Return something else to paint better
	return final

def find_brushhead(primary_color):
	pass



if __name__ == "__main__":
    main()