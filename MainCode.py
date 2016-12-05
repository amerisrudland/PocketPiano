import cv2
import numpy as np
import RPi.GPIO as GPIO
import time
from picamera.array import PiRGBArray
from picamera import PiCamera
import pygame
import csv
import pickle

#Initialize pygame and load sounds (for sound playing)
pygame.init()
pygame.mixer.music.load("Quack.wav")


#TURN ON THE LASER
laserLinePin = 18
#GPIO.BCM and GPIO.BOARD indicate different pin numbering conventions depending on the Raspberry Pi version
GPIO.setmode(GPIO.BCM) 
#Disables warnings
GPIO.setwarnings(False)
#Sets the pin as an output pin
GPIO.setup(laserLinePin, GPIO.OUT)
#Turn pin on (default is 3.3V)
GPIO.output(laserLinePin, GPIO.HIGH)

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
#cv2.namedWindow('HSV')

# Starting with 100's to prevent error while masking
h,s,v = 137,58,137

# Creating track bar Prev: 142,64,161
# the first integer parameter are the starting values

#cv2.createTrackbar('h', 'HSV',137,179,nothing)
#cv2.createTrackbar('s', 'HSV',58,255,nothing)
#cv2.createTrackbar('v', 'HSV',137,255,nothing)

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
notes = pickle.load ( open("CalibrationData.p", "rb"))

#creating masks from calibration data
white = (255,255,255)
teal = (161,232,9)
noteRegions = []
for idx,note in enumerate(notes):
    noteRegions.append(np.zeros((480,640),np.uint8))
    cv2.fillPoly(noteRegions[idx], [np.int32(note)],white)


#IMPORTANT
#OPEN CV uses BGR instead of RGB
#OPEN CV HSV values range from H = 0-180, S = 0-255 and V = 0-255. Scale accordingly

#MAIN LOOP

for frameRaw in camera.capture_continuous(rawCapture, format="bgr",use_video_port=True):

    frame = frameRaw.array
    
    #draw note regions in frame
    for note in notes:
        cv2.polylines(frame, [np.int32(note)],1,teal)
        # Convert BGR to HSV
    hsv= cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    # get info from track bar and appy to result
    #h = cv2.getTrackbarPos('h','HSV')
    #s = cv2.getTrackbarPos('s','HSV')
    #v = cv2.getTrackbarPos('v','HSV')

    #creates a mask with a lower threshold using the hsv values
    #and upper threshold of 180,255,255
    lowerRange = np.array([h,s,v])
    upperRange = np.array([180,255,255]) 
    mask = cv2.inRange(hsv, lowerRange, upperRange)
    
    # Bitwise-AND mask and original image
    result = cv2.bitwise_and(frame,frame, mask= mask)
    #The blurred image to reduce noise (higher number = more blurred; Must be odd number)
    blurredMask = cv2.medianBlur(mask,7)
    blurred = cv2.medianBlur(result,7)

    keypoints = []

    #OPTIMIZE THIS LOOP
    #print 'region size: {0}'.format(noteRegions[0].shape)
    #print 'blurredMask size: {0}'.format(blurredMask.shape)
    for region in noteRegions:
        searchArea = cv2.bitwise_and(blurredMask,blurredMask,mask = region)
        keypoints.append(detector.detect(searchArea))
        # We want to search just the region not the whole picture to speed up
        # keypoints.append(detector.detect(blurredMask,region)) # Maybe something like this?

    #Draw detected blobs as red circles
    #frameWithKeypoints = cv2.drawKeypoints(frame,keypoints,np.array([]), (0,0,255),cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
 

    #Check if regions are detecting keypoints
    for idx,keys in enumerate(keypoints):
        if keys:
            frame=cv2.drawKeypoints(frame,keys,np.array([]), teal, cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
            print 'keypoint detected in region {0}'.format(idx)
            
    #show images (i.e the frames
    #cv2.imshow("Keypoints", frameWithKeypoints)
    #cv2.imshow('de-noised',blurred)
    cv2.imshow('frame',frame)
    #cv2.imshow('mask',mask)
    #cv2.imshow('region0',noteRegions[0])
    #cv2.imshow('result',result)
    k = cv2.waitKey(1) & 0xFF
    if k == 27:
        break
    
    #clear keypoints
    keypoints[:]=[]
    rawCapture.truncate(0)

cv2.destroyAllWindows()
