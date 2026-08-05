from pathlib import Path

import cv2


def main():
    file_path = Path(__file__).parent
    print("안녕하세요.")
    print(cv2.__version__)
    img = cv2.imread(str(file_path / "data/robot.jpg"), cv2.IMREAD_GRAYSCALE)
    print(type(img), img.shape, img.dtype)
    img = img.reshape((500, 2000))  # 500,height,y ... 2000, width, x
    x = img.shape[1]
    y = img.shape[0]
    print(x, y)
    cv2.imshow("robot", img)

    cv2.imwrite(str(file_path / "data" / "robot_gray.jpg"), img)
    imwrite_op = [cv2.IMWRITE_JPEG_QUALITY, 10]
    cv2.imwrite(str(file_path / "data" / "robot_gray_10.jpg"), img, imwrite_op)
    cv2.imwrite(str(file_path / "data" / "robot_gray.bmp"), img)
    cv2.waitKey()


if __name__ == "__main__":
    main()
