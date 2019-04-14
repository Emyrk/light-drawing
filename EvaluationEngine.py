import cv2
import numpy as np

EVALUATION_SIZE_1 = (64, 64)
EVALUATION_SIZE_2 = (16, 16)
SCORE_MAX = 50

class EvaluationEngine:
    harshness = 1.0

    def __init__(self, harshness=1.0):
        """
        The EvaluationEngine evaluates a drawing compared to a target image.
        When constructing, you can set the harshness to a value between 0.0 and 5.0 (or higher)
        Normal harshness defaults to 1.0
        A harsher evaluation is 1.5
        An easier evaluation is 0.5


        :param harshness: value determining the harshness
        """
        self.harshness = harshness

    def evaluate(self, target, drawing, max_time, draw_time):
        """
        This compares two images, and returns the similarity
        as a number between 0 and 1.

        :param target: the target image
        :param drawing: the drawing image
        :return: value between 0 and 1 representing the similarity
        """

        # pre-process each image
        target_p = self._pre_process(target)
        drawing_p = self._pre_process(drawing)

        # calculate the amount the drawing missed
        # (didn't fill in the lines)
        missing = cv2.subtract(target_p, drawing_p)
        missing_sum = np.sum(missing)/255

        # calculate the amount the drawing added
        # (colored outside the lines)
        extra = cv2.subtract(drawing_p, target_p)
        extra_sum = np.sum(extra) / 255

        # calculate the total number of pixels desired
        target_sum = np.sum(target_p) / 255

        # compute the accuracy
        total_wrong_pixels = (missing_sum + extra_sum)/2
        total_wrong_pixels = min((total_wrong_pixels * self.harshness), target_sum)
        accuracy = 1.0 - (total_wrong_pixels/(target_sum))

        score = (SCORE_MAX * accuracy * (1.0 - (draw_time/max_time)))

        return (accuracy, score)


    def _pre_process(self, img):
        """
        This pre-processes an image before comparing it. The images we
        compare in the end are only 16x16 binary images. By downsampling and
        thresholding, we are baking a fuzziness into the comparison

        :param img: image to pre-process
        :return: the pre-processed image
        """
        pimg = cv2.resize(img, EVALUATION_SIZE_1)
        pimg = cv2.dilate(pimg, cv2.getStructuringElement(cv2.MORPH_DILATE, (3, 3)))
        pimg = cv2.resize(pimg, EVALUATION_SIZE_2)
        pimg = cv2.threshold(pimg, 30, 255, cv2.THRESH_BINARY)[1]

        return pimg
