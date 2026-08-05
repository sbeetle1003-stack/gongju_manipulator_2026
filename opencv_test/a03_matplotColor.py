# pip install matplotlib

from pathlib import Path

import cv2
from matplotlib import pyplot as plt


def main():
    file_path = Path(__file__).parent
    img = cv2.imread(str(file_path / "data/robot.jpg"))
    cv2.imshow("robot", img)
    plt.axis("off")
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    plt.imshow(imgRGB)
    cv2.waitKey(30)
    plt.show()


if __name__ == "__main__":
    main()
