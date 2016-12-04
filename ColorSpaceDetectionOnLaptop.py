#This code is kept to demonstrate how the camera code differs between laptop cameras and the Raspberry Pi camera

import cv2
import numpy as np
cap = cv2.VideoCapture(0)
while(1):
    # Take each frame
    _, frame = cap.read()
    # Convert BGR to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    # define range of blue color in BGR
    lower_blue = np.array([17,15,100])
    upper_blue = np.array([57,57,255])
    # Threshold the HSV image to get only blue colors
    mask = cv2.inRange(frame,lower_blue, upper_blue)
    # Bitwise-AND mask and original image
    res = cv2.bitwise_and(frame,frame, mask= mask)
    blurred = cv2.medianBlur(frame,7)
    cv2.imshow('blurred',blurred)
    cv2.imshow('frame',frame)
    cv2.imshow('mask',mask)
    cv2.imshow('res',res)
    k = cv2.waitKey(5) & 0xFF
    if k == 27:
        break
cv2.destroyAllWindows()

