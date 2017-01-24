import cv2
import numpy as np
import RPi.GPIO as GPIO
import time
from picamera.array import PiRGBArray
from picamera import PiCamera
import pygame
import csv
import pickle

def main():
    startTime=time.time()

    #define colors
    white = (255,255,255)
    teal = (161,232,9)

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
    time.sleep(1)

    #CREATE TRACKBARS TO CONTROL HSV

    def nothing(x):
        pass

    # Starting with 100's to prevent error while masking
    h,s,v = 137,58,137

    #IMPORTANT
    #OPEN CV uses BGR instead of RGB
    #OPEN CV HSV values range from H = 0-180, S = 0-255 and V = 0-255. Scale accordingly
    #Take a single screenshot
    camera.capture(rawCapture,format="bgr",use_video_port=True)
    laserOnPhoto=rawCapture.array
    #Turn laser off
    GPIO.output(laserLinePin, GPIO.LOW)
    #wait for laser to turn off
    time.sleep(0.05)
    #Take a single screenshot
    rawCapture.truncate(0)
    camera.capture(rawCapture,format="bgr",use_video_port=True)
    laserOffPhoto=rawCapture.array

    #Wait a second and do it all again
    GPIO.output(laserLinePin, GPIO.HIGH)
    time.sleep(1)
    rawCapture.truncate(0)
    camera.capture(rawCapture,format="bgr",use_video_port=True)
    laserOnPhoto2=rawCapture.array
    #Turn laser off
    GPIO.output(laserLinePin, GPIO.LOW)
    #wait for laser to turn off
    time.sleep(0.05)
    #Take a single screenshot
    rawCapture.truncate(0)
    camera.capture(rawCapture,format="bgr",use_video_port=True)
    laserOffPhoto2=rawCapture.array

    #FOR MADDY
    #Take photo with corners
    #project image with corners shown
    #camera.capture(rawCapture,format="bgr",use_video_port=True)
    #withCorners=rawCapture.array
    #Take photo without corners
    #project iamge without corners shown
    #rawCapture.truncate(0)
    #camera.capture(rawCapture,format="bgr",use_video_port=True)
    #withoutCorners=rawCapture.array
    #Get the difference of the two images
    #difference=absdiff(withCorners,withoutCorners)
    #create blob detector (reference blob detector construction in main code)
    #keypoints=detector.detect(difference)
    #get coordinates of 4 corners
    #for point in keyponts
    #    corners = point.x,point.y

    #Create background subtractor using image without laser
    #fgbg = cv2.BackgroundSubtractor.apply(laserOnPhoto,laserOffPhoto)
    #fgmask = fgbg.apply(laserOffPhoto)
    #cv2.imshow("backgroundsubtractormask",fgmask);

    #increase contrast
    #laserOffPhoto=laserOffPhoto*5
    #laserOnPhoto=laserOnPhoto*5

    difference=cv2.absdiff(laserOffPhoto,laserOnPhoto)
    differenceHighContrast=difference*3
    test=laserOnPhoto-laserOnPhoto

    #Convert difference image into mask
    lowerRange = np.array([15,15,15])
    upperRange = np.array([180,255,255])
    hsv = cv2.cvtColor(differenceHighContrast, cv2.COLOR_BGR2HSV)
    differenceMask = cv2.inRange(hsv,lowerRange,upperRange)
    differenceMask = cv2.medianBlur(differenceMask,7)


    difference=cv2.absdiff(laserOffPhoto2,laserOnPhoto2)
    differenceHighContrast=difference*3
    differenceHighContrast=cv2.bitwise_and(differenceHighContrast,differenceHighContrast,mask= differenceMask)
    hsv = cv2.cvtColor(differenceHighContrast, cv2.COLOR_BGR2HSV)
    
    differenceMask = cv2.inRange(hsv,lowerRange,upperRange)
    differenceMask = cv2.medianBlur(differenceMask,7)

    justLasers = cv2.bitwise_and(laserOnPhoto,laserOnPhoto,mask= differenceMask)
    

    cv2.imshow("test - this should be completely black",test)
    
    cv2.imshow("Laser On",laserOnPhoto)
    cv2.imshow("Laser Off",laserOffPhoto)
    cv2.imshow("difference",difference)
    cv2.imshow("differenceHighContrast",differenceHighContrast)
    cv2.imshow("Mask",differenceMask)
    cv2.imshow("Just Laser",justLasers)

    justLasersHSV=cv2.cvtColor(justLasers,cv2.COLOR_BGR2HSV)
    
    #print(justLasers)
    #print(justLasers.ndim)
    upperRange=np.amax(np.amax(justLasers,axis=0),axis=0)
    print(upperRange)
    lowerRange=upperRange-120
    print(lowerRange)

    hsv=cv2.cvtColor(differenceHighContrast,cv2.COLOR_BGR2HSV)
    finalMask = cv2.inRange(hsv,lowerRange,upperRange)
    refinedDifferenceHighContrast = cv2.bitwise_and(differenceHighContrast,differenceHighContrast,mask= finalMask)
    cv2.imshow("refinedDifferenceHighContrast",refinedDifferenceHighContrast)

    hsv=cv2.cvtColor(refinedDifferenceHighContrast,cv2.COLOR_BGR2HSV)
    lowerRange=np.array([10,10,10])
    upperRange=np.array([180,255,255])
    
    finalMask=cv2.inRange(hsv,lowerRange,upperRange)
    hsv=cv2.cvtColor(laserOnPhoto,cv2.COLOR_BGR2HSV)
    result=cv2.bitwise_and(laserOnPhoto,laserOnPhoto,mask= finalMask)
    cv2.imshow("res",result)
    cv2.imshow("refinedDifferenceHighContrastMask",finalMask)

    
    
    #MAIN LOOP TO DISPLAY WINDOWS

    while True:
        #Check for keyboard press and assign key pressed (if any) to k
        k = cv2.waitKey(1) & 0xFF
        if k == 27: #escape key
            break
        if k == 49: #1 key
            showFrame = not showFrame
        if k == 50: #2 key
            showRes = not showRes
        if k == 51: #3 key
            showWholeFrame= not showWholeFrame
        if k == 52: #4 key
            showMask = not showMask
        if k == 53: #5 key
            showFrameRate = not showFrameRate
        if k == 54: #6 key
            playSounds = not playSounds


    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
