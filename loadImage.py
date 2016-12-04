import numpy
import cv2

img = cv2.imread("test.png")
cv2.imshow("OH YAY!", img)
print img.shape
cv2.waitKey(0)
