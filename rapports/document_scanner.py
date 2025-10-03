import cv2
import imutils


def check_image_requirements(path):

    # loading image
    image = cv2.imread(path)

    ### convert the image to grayscale, blur it, and find edges in the image
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Gaussian Blurring to remove high frequency noise helping in
    # Contour Detection
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    # Canny Edge Detection
    edged = cv2.Canny(gray, 0, 10)

    cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Handling due to different version of OpenCV
    cnts = cnts[0] if imutils.is_cv2() else cnts[1]

    # Taking only the top 5 contours by Area
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:5]

    # looping over the contours
    for c in cnts:
        ### Approximating the contour

        # Calculates a contour perimeter or a curve length
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.01 * peri, True)  # 0.02

        # if our approximated contour has four points, then we
        # can assume that we have found our screen
        screenCnt = approx
        if len(approx) == 4:
            screenCnt = approx
            break

    if len(screenCnt) < 6:
        return True


