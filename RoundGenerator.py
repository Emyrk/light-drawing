import cv2
import Config
import numpy as np

class RoundGenerator:

    # (target image, seconds to play)
    rounds = [
        ("circle.png", 10),
        ("square.png", 10),
        ("rectangle.png", 10),
        ("triangle.png", 10),
        ("disney.png", 15),
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
        img = cv2.imread("round_images/" + img_name, cv2.IMREAD_GRAYSCALE)

        # convert to binary image
        img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)[1]

        # scale image to world coordinates
        img = cv2.resize(img, Config.WORLD_SPACE_SIZE)

        # sharpen image (https://stackoverflow.com/questions/4993082/how-to-sharpen-an-image-in-opencv)
        kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
        img = cv2.filter2D(img, -1, kernel)

        # invert image so border is 255, and background is 0
        img = (255 - img)

        # return image
        return img
