import cv2
import Config
import numpy as np

class RoundGenerator:

    # (target image, seconds to play)
    rounds = [
        ("circle.png", 3),
        ("square.png", 5),
        ("rectangle.png", 5),
        ("triangle.png", 5)
    ]

    @staticmethod
    def get_round(round_number):
        """
        Get the next image
        :return: (target image in world size, seconds to play)
        """
        round = RoundGenerator.rounds[(round_number) % len(RoundGenerator.rounds)]
        img = RoundGenerator.get_image(round[0])
        return (img, round[1])

    @staticmethod
    def get_image(img_name):
        """
        Read in image and pre-process it

        :param img_name: image name to read in
        :return: pre-processed image in world size
        """
        # read in image
        img = cv2.imread("round_images/" + img_name)

        # scale image to world coordinates
        img = cv2.resize(img, Config.WORLD_SPACE_SIZE)

        # sharpen image (https://stackoverflow.com/questions/4993082/how-to-sharpen-an-image-in-opencv)
        kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
        img = cv2.filter2D(img, -1, kernel)

        # return image
        return img

    @staticmethod
    def display_image(img):
        """
        Just used for debugging
        :param img:
        :return:
        """
        cv2.namedWindow("win", cv2.WINDOW_NORMAL)
        cv2.imshow("win", img)
        cv2.waitKey(0)
