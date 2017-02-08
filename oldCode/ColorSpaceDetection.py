import cv2
import numpy as np
import RPi.GPIO as GPIO
import time
from picamera.array import PiRGBArray
from picamera import PiCamera

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

def nothing(x):
    pass
# Creating a window for later use
cv2.namedWindow('result')

# Starting with 100's to prevent error while masking
h,s,v = 100,100,100

# Creating track bar Prev: 142,64,161

cv2.createTrackbar('h', 'result',128,179,nothing)
cv2.createTrackbar('s', 'result',109,255,nothing)
cv2.createTrackbar('v', 'result',200,255,nothing)



#IMPORTANT
#OPEN CV uses BGR instead of RGB
#OPEN CV HSV values range from H = 0-180, S = 0-255 and V = 0-255. Scale accordingly

for frameRaw in camera.capture_continuous(rawCapture, format="bgr",use_video_port=True):
    frame = frameRaw.array
    # Convert BGR to HSV
    hsv= cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    # get info from track bar and appy to result
    h = cv2.getTrackbarPos('h','result')
    s = cv2.getTrackbarPos('s','result')
    v = cv2.getTrackbarPos('v','result')

    lower_red = np.array([h,s,v]) # 0 50 50
    upper_red = np.array([180,255,255])  # 10 255 255
    mask0 = cv2.inRange(hsv, lower_red, upper_red)
    
    # upper mask (170-180) for upper thresholdof red
    lower_red = np.array([61,13,150])
    upper_red = np.array([0,0,255])
    mask1 = cv2.inRange(hsv, lower_red, upper_red)

    # combine 
    mask = mask0#+mask1
    
    # Bitwise-AND mask and original image
    result = cv2.bitwise_and(frame,frame, mask= mask)
    #The blurred image to reduce noise (higher number = more blurred; Must be odd number)
    blurred = cv2.medianBlur(result,7)

    #Get grey-scale image
    #grey_image = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)

    #cv2.imshow('de-noised',blurred)
    cv2.imshow('frame',frame)
    #cv2.imshow('mask',mask)
    cv2.imshow('result',result)
    k = cv2.waitKey(1) & 0xFF
    if k == 27:
        break
    
    rawCapture.truncate(0)

cv2.destroyAllWindows()
