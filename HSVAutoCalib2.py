import cv2
import numpy as np
import RPi.GPIO as GPIO
import time
from picamera.array import PiRGBArray
from picamera import PiCamera
import pygame
import csv
import pickle

def calib(camera,rawCapture,laserLinePin):

    def nothing(x):
        pass

    # Starting with 100's to prevent error while masking
    h,s,v = 137,58,137

    #Turn on laser
    GPIO.output(laserLinePin, GPIO.HIGH)
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

    #Take difference of pair of laser photos
    difference=cv2.absdiff(laserOffPhoto,laserOnPhoto)
    #Increase contrast
    differenceHighContrast=difference*3

    #Convert difference image into mask
    lowerRange = np.array([15,15,15])
    upperRange = np.array([180,255,255])
    hsv = cv2.cvtColor(differenceHighContrast, cv2.COLOR_BGR2HSV)
    differenceMask = cv2.inRange(hsv,lowerRange,upperRange)
    differenceMask = cv2.medianBlur(differenceMask,7)

    #Get difference of second pair of laser photos taken
    difference=cv2.absdiff(laserOffPhoto2,laserOnPhoto2)
    differenceHighContrast=difference*3

    #Apply mask from first two images, to difference of second two images (helps remove noise)
    differenceHighContrast=cv2.bitwise_and(differenceHighContrast,differenceHighContrast,mask= differenceMask)

    #Convert to grayscale
    differenceHighContrastGray=cv2.cvtColor(differenceHighContrast, cv2.COLOR_BGR2GRAY)
 

    #find average value in grayscale image to identify threshold for binary thresholding
    total=0
    count=0
    for pixelLine in differenceHighContrastGray:
        for pixel in pixelLine:
            if pixel>0:
                total=total+pixel
                count=count+1
    thresh=total/count
    #thresh = 50

    #Apply a binary threshold to create a mask covering only exactly the laser, using the grayscale image
    maxValue = 255
    _,refinedMask=cv2.threshold(differenceHighContrastGray,thresh,maxValue,cv2.THRESH_BINARY)


    #Apply the refined mask to the difference image
    differenceJustLasers=cv2.bitwise_and(differenceHighContrast,differenceHighContrast,mask= refinedMask)

    #Apply the refined mask to the original laserOnPhoto
    res=cv2.bitwise_and(laserOnPhoto,laserOnPhoto,mask= refinedMask)

    #cv2.imshow("greyscale",differenceHighContrastGray)
    #cv2.imshow("Laser On",laserOnPhoto)
    #cv2.imshow("Laser Off",laserOffPhoto)
    #cv2.imshow("difference",difference)
    #cv2.imshow("differenceHighContrast",differenceHighContrast)
    #cv2.imshow("Original Mask",differenceMask)
    #cv2.imshow("refined mask",refinedMask)
    #cv2.imshow("Just laser in difference image",differenceJustLasers)
    #cv2.imshow("result (just lasers)",res)


    #convert res to hsv
    res = cv2.cvtColor(res,cv2.COLOR_BGR2HSV)
    #iterate through resulting image to find lower and upper hsv values
    lowerRange=(180,255,255)
    for pixelLine in res:
        for pixel in pixelLine:
            if pixel.all() != 0 and pixel[0] < lowerRange[0] and pixel[1] < lowerRange[1] and pixel[2] < lowerRange[2]:
                lowerRange=pixel


    GPIO.output(laserLinePin, GPIO.HIGH)
    print(lowerRange)
    rawCapture.truncate(0)
    return np.array([lowerRange[0]+1,lowerRange[1]+1,lowerRange[2]+1])

    
    
    

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

    upperRange=np.array([180,255,255])
    
    # allow the camera to warmup
    time.sleep(1)
    lowerRange=calib(camera,rawCapture,laserLinePin)
    GPIO.output(laserLinePin, GPIO.HIGH)

    #MAIN LOOP TO DISPLAY WINDOWS
    rawCapture.truncate(0)
    for frameRaw in camera.capture_continuous(rawCapture, format="bgr",use_video_port=True):


        frame = frameRaw.array
        

        hsv= cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        #creates a mask with a lower threshold using the hsv values
        #and upper threshold of 180,255,255
        mask = cv2.inRange(hsv, lowerRange, upperRange)
        #The blurred image to reduce noise (higher number = more blurred; Must be odd number)
        mask = cv2.medianBlur(mask,7)
        
        # Bitwise-AND mask and original image
        result = cv2.bitwise_and(frame,frame, mask= mask)
        cv2.imshow('result',result)
        cv2.imshow('frame',frame)
            
        #The blurred image to reduce noise (higher number = more blurred; Must be odd number)
        #blurredMask = cv2.medianBlur(mask,7)

    
        
        #Check for keyboard press and assign key pressed (if any) to k
        k = cv2.waitKey(1) & 0xFF
        if k == 27: #escape key
            break
        
        rawCapture.truncate(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
