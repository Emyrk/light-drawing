from DebugUtils import display_all_img
import cv2
import numpy as np
import math
import pandas as pd


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
        points = DrawingEngine._smooth(points)
        if len(points) == 0:
            return
        for i in range(1, len(points)):
            if points[i - 1] is None or points[i] is None:
                continue
            DrawingEngine._draw_line(img, points[i-1], points[i], color)

    @staticmethod
    def _smooth(points):
        size = 3
        if len(points) < size:
            return points
        unzipped = list(zip(*points))
        xs = list(unzipped[0])
        ys = list(unzipped[1])
        xs = pd.DataFrame(xs).rolling(size, min_periods=1).mean()
        xs = np.array((xs[xs.columns[0]]))
        ys = pd.DataFrame(ys).rolling(size, min_periods=1).mean()
        ys = np.array((ys[ys.columns[0]]))
        xs = xs.astype(int)
        ys = ys.astype(int)

        return list(zip(xs, ys))


    @staticmethod
    def _blank_img_of_size(img_wid, img_hei):
        return np.zeros((img_hei, img_wid, 3), np.uint8)

    @staticmethod
    def _blank_1_ch_img_of_size(img_wid, img_hei):
        return np.zeros((img_hei, img_wid), np.uint8)


# Use this
# display_all_img([DrawingEngine.draw([(0,0), (50,50)], 500, 500, (22, 33, 89))])