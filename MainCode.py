import cv2
import numpy as np
import RPi.GPIO as GPIO
import time
from picamera.array import PiRGBArray
from picamera import PiCamera
import pygame
import csv
import pickle

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

cv2.createTrackbar('h', 'result',137,179,nothing)
cv2.createTrackbar('s', 'result',58,255,nothing)
cv2.createTrackbar('v', 'result',137,255,nothing)

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

#gets all points in notes and puts them in a single point array
allNotePoints = []
for note in notes:
    for point in note:
        allNotePoints.append(point)

#Get bounding rectangle around all notes
pianoX,pianoY,pianoWidth,pianoHeight = cv2.boundingRect(np.array(allNotePoints))

#Because we are now taking a subsection of the frame, we need to offset all note regions for the new
#co-ordinate system
offsetNotes = []
offsetNote = []
for note in notes:
    offsetNote[:] = []
    for point in note:
        offsetNote.append((point[0]-pianoX,point[1]-pianoY))
    offsetNotes.append(list(offsetNote))

notes = offsetNotes

#IMPORTANT
#OPEN CV uses BGR instead of RGB
#OPEN CV HSV values range from H = 0-180, S = 0-255 and V = 0-255. Scale accordingly

print'Time to start up: {0} seconds'.format(time.time() - startTime)

#Boolean values to indicate what operations to conduct
showRes=True
showWholeFrame=False
showFrame=True
showMask=False
showFrameRate = False
playSounds = True

#Initalize the mixer
pygame.mixer.init()
#Set number of channels
pygame.mixer.set_num_channels(13)

#Initialize the array of notes
notesList = []
notesList.append(pygame.mixer.Sound("Quack.wav"))
notesList.append(pygame.mixer.Sound("cow.wav"))
notesList.append(pygame.mixer.Sound("hello.wav"))
notesList.append(pygame.mixer.Sound("welcome.wav"))
notesList.append(pygame.mixer.Sound("goodbye.wav"))
notesList.append(pygame.mixer.Sound("bird.wav"))
notesList.append(pygame.mixer.Sound("Quack.wav"))
notesList.append(pygame.mixer.Sound("cow.wav"))
notesList.append(pygame.mixer.Sound("hello.wav"))
notesList.append(pygame.mixer.Sound("welcome.wav"))
notesList.append(pygame.mixer.Sound("goodbye.wav"))
notesList.append(pygame.mixer.Sound("bird.wav"))
notesList.append(pygame.mixer.Sound("Quack.wav"))



#MAIN LOOP

for frameRaw in camera.capture_continuous(rawCapture, format="bgr",use_video_port=True):
    if showFrameRate == True:
        startTime = time.time()

    wholeFrame = frameRaw.array
    #get region of interest using bounding rect (just the part of the frame with piano
    frame = wholeFrame[pianoY:pianoY+pianoHeight,pianoX:pianoX+pianoWidth]
    
    #draw note regions in frame
    for note in notes:
        cv2.polylines(frame, [np.int32(note)],1,teal)
        # Convert BGR to HSV
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
    
    #check all noteRegions for keypoints
    #for idx,region in enumerate(notes):
    if playSounds == True:
        for idx,region in enumerate(notes):
            for key in keypoints:
               if cv2.pointPolygonTest(np.array(region),key.pt,False)  == 1.0:
                   #THIS IS WHERE WE PLAY SOUNDS :D
                    print 'Region {0} is triggered'.format(idx)
                    #if the channel is not in use, play the sound
                    #code is setup so each note gets it's own channel
                    channel = pygame.mixer.Channel(idx)
                    if not channel.get_busy():
                        channel.play(notesList[idx])
                    #notesList[idx].play()
                    #wait for sound to finish playing
                    #while pygame.mixer.music.get_busy():
                        #time.sleep(0.1)
                    
    #show images (i.e the frames)
    if showFrame == True:
        frame= cv2.drawKeypoints(frame,keypoints,np.array([]), (0,0,255),cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        cv2.imshow('piano',frame)
    if showWholeFrame == True:
        cv2.imshow('frame',wholeFrame)
    if showMask == True:
        cv2.imshow('mask',mask)
    
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
    
    #clear keypoints
    keypoints[:]=[]
    rawCapture.truncate(0)

    if showFrameRate == True:
        print 'Frame rate: {0} seconds'.format(time.time()-startTime)

cv2.destroyAllWindows()
