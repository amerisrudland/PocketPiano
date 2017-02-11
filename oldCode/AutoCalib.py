import cv2
import numpy as np
import RPi.GPIO as GPIO
import time
from picamera.array import PiRGBArray
from picamera import PiCamera
import pygame
import csv
import pickle
import math

numWhiteKeys = 8
numBlackKeys = 5
startTime=time.time()

#define colors
white = (255,255,255)
teal = (161,232,9)

#TURN ON VIDEO FEED
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(640, 480))
 
# allow the camera to warmup
time.sleep(0.1)

#CREATE TRACKBARS TO CONTROL HSV

def nothing(x):
    pass
# Creating a window for later use
cv2.namedWindow('result')

# Starting with 100's to prevent error while masking
h,s,v = 137,58,137

# Creating track bar Prev: 142,64,161
# the first integer parameter are the starting values

cv2.createTrackbar('h', 'result',61,179,nothing)
cv2.createTrackbar('s', 'result',85,255,nothing)
cv2.createTrackbar('v', 'result',101,255,nothing)

#SETUP BLOB DETECTION
#http://www.learnopencv.com/blob-detection-using-opencv-python-c/
# Setup SimpleBlobDetector parameters.
params = cv2.SimpleBlobDetector_Params()
 
# Change thresholds
params.minThreshold = 0;
params.maxThreshold = 500;


# Filter by Color
params.filterByColor = True
params.blobColor=255
 
# Filter by Area.
params.filterByArea = False
params.minArea = 50
params.maxArea = 500
 
# Filter by Circularity
params.filterByCircularity = False
params.minCircularity = 0.1
 
# Filter by Convexity
params.filterByConvexity = False
params.minConvexity = 0.87
 
# Filter by Inertia
params.filterByInertia = False
params.minInertiaRatio = 0.01
 
# Create a detector with the parameters
detector = cv2.SimpleBlobDetector_create(params)

#IMPORTING CALIBRATION DATA
data = pickle.load ( open("CalibrationData.p", "rb"))

pts = []
for corners in data:
    for corner in corners:
        pts.append(corner)
print pts
pts = sorted(pts)   #LowerLeft, UpperLeft, UpperRight, LowerRight
print pts
print pts[0][0]

bottomWidth = (pts[3][0] - pts[0][0])/8.0
bottomHeight = (pts[3][1] - pts[0][1])/8.0

topWidth = (pts[2][0] - pts[1][0])/8.0
topHeight = (pts[2][1] - pts[1][1])/8.0

blackBW = bottomWidth/4.0
blackBH = bottomHeight/4.0
blackTW = topWidth/4.0
blackTH = topHeight/4.0

keys=[]
keyNum = 1
pt0 = []
pt1 = []
pt2 = []
pt3 = []
pt4 = []
pt5 = []
pt6 = []

while keyNum <= numWhiteKeys:
    if keyNum == 1:
        pt0 = pts[0]
        pt1 = pts[1]
        pt2 = [pt1[0] + topWidth, pt1[1] + topHeight]
        pt3 = [pt0[0] + bottomWidth, pt0[1] + bottomHeight]
        pt4 = pt3
        pt5 = pt3
        pt6 = pt3

    else:
        pt0 = pt3
        pt1 = pt2
        pt2 = [pt1[0] + topWidth, pt1[1] + topHeight]
        pt3 = [pt0[0] + bottomWidth, pt0[1] + bottomHeight]

        if keyNum <= 4:
            pt4 = [pt3[0] + abs((pt2[0]-pt3[0])*2/3), pt3[1] - abs((pt2[1]-pt3[1])*2/3)]
            pt5 = [pt4[0] - blackTW, pt4[1] - blackTH]
        elif keyNum is not 5 and keyNum is not 8:
            pt4 = [pt2[0] + abs((pt2[0]-pt3[0])*2/3)/2, pt3[1] - abs((pt2[1]-pt3[1])*2/3)]

        if keyNum is 2 or keyNum is 3 or keyNum is 4 or keyNum is 6 or keyNum is 7:
            pt5 = [pt4[0] - blackTW, pt4[1] - blackTH]
            pt6 = [pt3[0]- blackTW, pt3[1] - blackTH]
        else:
            pt5 = pt3
            pt6 = pt3

    key = []
    key.append(pt0)
    key.append(pt1)
    key.append(pt2)
    key.append(pt3)
    key.append(pt4)
    key.append(pt5)
    key.append(pt6)
    keys.append(key)

    keyNum += 1
print keys

showRes=True
showWholeFrame=True
showFrame=False
showMask=False
showFrameRate = False
playSounds = False


for frameRaw in camera.capture_continuous(rawCapture, format="bgr",use_video_port=True):
    if showFrameRate == True:
        startTime = time.time()

    wholeFrame = frameRaw.array
    frame = wholeFrame
    color = (255,255,255)
    for key in keys:
        print key
        for x,y in key:
            #Draw cross at coordinates
            x = int(x)
            y = int (y)
            cv2.line(wholeFrame,(x,y-3),(x,y+3), color,2)
            cv2.line(wholeFrame,(x-3,y),(x+3,y), color,2)

        #cv2.line(wholeFrame, (key[0][0], key[0][1]), (key[1][0], key[1][1]), color, 1)
        #cv2.line(wholeFrame, (key[2][0], key[2][1]), (key[3][0], key[3][1]), color, 1)
        #cv2.line(wholeFrame, (key[1][0], key[1][1]), (key[2][0], key[2][1]), color, 1)
        #cv2.line(wholeFrame, (key[3][0], key[3][1]), (key[0][0], key[0][1]), color, 1)


    hsv= cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    if showRes == True:
        # get info from track bar and appy to result
        h = cv2.getTrackbarPos('h','result')
        s = cv2.getTrackbarPos('s','result')
        v = cv2.getTrackbarPos('v','result')
        

    #creates a mask with a lower threshold using the hsv values
    #and upper threshold of 180,255,255
    lowerRange = np.array([h,s,v])
    upperRange = np.array([180,255,255]) 
    mask = cv2.inRange(hsv, lowerRange, upperRange)
    #The blurred image to reduce noise (higher number = more blurred; Must be odd number)
    mask = cv2.medianBlur(mask,7)
    
    # Bitwise-AND mask and original image
    if showRes == True:
        result = cv2.bitwise_and(frame,frame, mask= mask)
        cv2.imshow('result',result)
        
    #The blurred image to reduce noise (higher number = more blurred; Must be odd number)
    #blurredMask = cv2.medianBlur(mask,7)

    keypoints = []

    #Get all keypoints in the image and print
    keypoints = detector.detect(mask)
    
                    
    #show images (i.e the frames)
    if showWholeFrame == True:
        cv2.imshow('frame',wholeFrame)
    if showMask == True:
        cv2.imshow('mask',mask)
    cv2.imshow('result',result)
    
    #clear keypoints
    keypoints[:]=[]
    rawCapture.truncate(0)

    if showFrameRate == True:
        print 'Frame rate: {0} seconds'.format(time.time()-startTime)

    k = cv2.waitKey(1) & 0xFF
    if k == 27: #escape key
        break

cv2.destroyAllWindows()
