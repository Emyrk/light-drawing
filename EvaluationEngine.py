import cv2
import numpy as np
from DebugUtils import display_all_img
from RoundGenerator import RoundGenerator

EVALUATION_SIZE_1 = (64, 64)
EVALUATION_SIZE_2 = (32, 32)
SCORE_MAX = 100

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

        # calculate the total number of pixels in target image
        target_sum = np.sum(target_p) / 255

        # calculate the number of correctly drawn pixels
        missing = cv2.subtract(target_p, drawing_p)
        missing_sum = np.sum(missing)/255
        correct_sum = target_sum - missing_sum

        # calculate the number of extra pixels drawn (not touching target)
        # (colored outside the lines)
        extra = cv2.subtract(drawing_p, target_p)
        extra_sum = np.sum(extra) / 255

        # of pixels drawn, what ratio ([0,1]) were on target?
        drawing_accuracy = correct_sum / max((correct_sum + extra_sum), 1)

        # what percent ([0,1]) of the image was filled in?
        image_completeness = correct_sum / max(target_sum, 1)

        # final accuracy percent ([0,1])
        accuracy = image_completeness * drawing_accuracy

        accuracy = max(min(accuracy - ((self.harshness - 1) * accuracy), 1.0), 0.0)

        # display_all_img([target, drawing, missing, extra])

        score = (SCORE_MAX * accuracy)

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


# e = EvaluationEngine(0.7)
# e.evaluate(RoundGenerator.get_round(3)[0], RoundGenerator.get_round(4)[0], 5, 5)
