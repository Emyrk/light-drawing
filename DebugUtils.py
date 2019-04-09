import cv2

def display_image(img):
    """
    Just used for debugging
    :param img: image to display
    :return:
    """
    cv2.namedWindow("debug_win", cv2.WINDOW_NORMAL)
    cv2.imshow("debug_win", img)
    cv2.waitKey(0)
