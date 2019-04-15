from DebugUtils import display_all_img
import cv2
import numpy as np
import math


class DrawingEngine:
    @staticmethod
    def draw(points, img_wid, img_hei, color):
        img = DrawingEngine._blank_img_of_size(img_wid, img_hei)
        DrawingEngine._draw_lines(img, points, color)
        return img

    @staticmethod
    def draw_binary(points, img_wid, img_hei):
        img = DrawingEngine._blank_1_ch_img_of_size(img_wid, img_hei)
        DrawingEngine._draw_lines(img, points, 255)
        return img

    @staticmethod
    def _draw_line(img, p1, p2, color):
        cv2.line(img, p1, p2, color, thickness=20, lineType=8)

    @staticmethod
    def _draw_lines(img, points, color):
        if len(points) == 0:
            return
        last_point = points[0]
        for i in range(1, len(points)):
            if points[i - 1] is None or points[i] is None:
                continue
            x1 = last_point[0]
            x2 = points[i][0]
            y1 = last_point[1]
            y2 = points[i][1]
            pythag = math.sqrt(pow(abs(x1-x2), 2) + pow(abs(y1-y2), 2))

            # Only draw if at least 10 pixels away from last point
            if (pythag > 10):
                DrawingEngine._draw_line(img, last_point, points[i], color)
                last_point = points[i]

    @staticmethod
    def _blank_img_of_size(img_wid, img_hei):
        return np.zeros((img_hei, img_wid, 3), np.uint8)

    @staticmethod
    def _blank_1_ch_img_of_size(img_wid, img_hei):
        return np.zeros((img_hei, img_wid), np.uint8)


# Use this
# display_all_img([DrawingEngine.draw([(0,0), (50,50)], 500, 500, (22, 33, 89))])
