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

for frameRaw in camera.capture_continuous(rawCapture, format="bgr",use_video_port=True):
    frame = frameRaw.array

    cv2.imshow("cameraFeed",frame)
    k = cv2.waitKey(1) & 0xFF
    if k == 27:
        break
    
    rawCapture.truncate(0)

cv2.destroyAllWindows()
