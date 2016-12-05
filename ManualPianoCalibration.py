import cv2
import numpy as np
import RPi.GPIO as GPIO
import time
from picamera.array import PiRGBArray
from picamera import PiCamera
import pygame
import copy
import csv
import pickle



#THIS CODE ALLOWS MANUAL CALIBRATION OF PIANO ZONES.
#Instructions:
#Use the left mouse button to select the vertices of the piano. When a key region has been created, use the right mouse
#button to fill in the region. A mask will be created to cover that region, and you can draw the next note.
#The mask regions are stored in a csv file which will be openned by MainCode.


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


#color of drawn shapes/text
color = (255,255,255)

shapes = []
points = []

#event: the event that took place (left mouse button pressed, left mouse button
#released etc.
#x: the x-coordinate of the event
#y: the y-coordinate of the event
#flags: any relevant flag passed by OpenCV
#params: Any extra parameters supplied by openCV
def click(event, x, y, flags, param):
    #reference points outside the function
    global points
    global shapes
    #Check if left mouse button was pressed
    if event == cv2.EVENT_LBUTTONDOWN:
        #Save coordinates in current points list
        points.append((x,y))
    #Check if right mouse button was pressed
    if event == cv2.EVENT_RBUTTONDOWN and points:
        #appends the current points list to the shapes list
        shapes.append(list(points))
        #empty points list
        points[:]=[]
cv2.namedWindow("image")
cv2.setMouseCallback("image", click)
#create all-black image
mask = np.zeros((480,640,3),np.uint8)

#MAIN LOOP

for frameRaw in camera.capture_continuous(rawCapture, format="bgr",use_video_port=True):
    image = frameRaw.array
    #Draw points at all points in the current points list
    for x,y in points:
        #Draw cross at coordinates
        cv2.line(image,(x,y-3),(x,y+3), color,2)
        cv2.line(image,(x-3,y),(x+3,y), color,2)
        #label coordinates
        cv2.putText(image, '{0},{1}'.format(x,y),(x-30,y-20),cv2.FONT_HERSHEY_DUPLEX,0.5,color,1)
    #draw shapes for every set of points in the shapes list
    for shape in shapes:
        cv2.fillPoly(mask, [np.int32(shape)],color)
        cv2.polylines(image, [np.int32(shape)],1,color)

    #show images (i.e the frames)
    cv2.imshow('image',image)
    cv2.imshow('mask',mask)
    k = cv2.waitKey(1) & 0xFF
    if k == 27:
        break
    rawCapture.truncate(0)

#Store calibrated data as csv
pickle.dump(shapes,open("CalibrationData.p","wb"))


cv2.destroyAllWindows()
