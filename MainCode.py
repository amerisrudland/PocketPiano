import cv2
import numpy as np
import RPi.GPIO as GPIO
import time
from picamera.array import PiRGBArray
from picamera import PiCamera
import pygame
import csv
import pickle
import setup
import FindPianoCorners
import piano_projection
import HSVAutoCalib2

TEAL = (161,232,9)

def calculate_key_points(keyboard_corners):
    # Calcluate dimensions of white and black keys
    correction_x = 1.0
    correction_y = 0.5
    bottomWidth = (keyboard_corners[3][0] - keyboard_corners[0][0])/8.0
    bottomHeight = (keyboard_corners[3][1] - keyboard_corners[0][1])/8.0

    topWidth = (keyboard_corners[2][0] - keyboard_corners[1][0])/8.0
    topHeight = (keyboard_corners[2][1] - keyboard_corners[1][1])/8.0

    blackBW = bottomWidth/4.0 + 2.0
    blackBH = bottomHeight/4.0
    blackTW = topWidth/4.0 + 1.0
    blackTH = topHeight/4.0

#   The key points are layed out as follows

#   1               2
#
#
#
#   7   8       5   4
#
#
#
#   0   9       6   3

    keys=[]
    black_key = []
    keyNum = 1

    while keyNum <= 8:
        # Calculate corners of white key
        if keyNum == 1:
            pt0 = keyboard_corners[0]
            pt1 = keyboard_corners[1]
        else:
            pt0 = pt3
            pt1 = pt2

        if keyNum <= 3:
            correctBW = 0.0#1.0
            correctBH = 0.0#1.0
            correctTW = 0.5
            correctTH = 0.5
        else:
            correctBW = 0.5
            correctBH = 0.5
            correctTW = 0.0#-0.25
            correctTH = 0.0#-0.25
            
        pt2 = [pt1[0] + topWidth + correctTW, pt1[1] + topHeight + correctTH]
        pt3 = [pt0[0] + bottomWidth + correctBW, pt0[1] + bottomHeight + correctBH]

        # Calculate corners of black key to the right
        if (pt2[0] > pt3[0]):    # Midpoint is right of bottom corner
            pt4 = [pt3[0] + abs((pt2[0]-pt3[0])*2/3), pt3[1] - abs((pt2[1]-pt3[1])*4/7)]
        else:
            pt4 = [pt2[0] + abs((pt2[0]-pt3[0])*2/3)/2, pt3[1] - abs((pt2[1]-pt3[1])*4/7)]

        pt5 = [pt4[0] - blackTW, pt4[1] - blackTH]
        pt6 = [pt3[0]- blackBW, pt3[1] - blackBH]

        # Calculate corners of black key to the left
        if (pt1[0] > pt0[0]):    # Midpoint is right of bottom corner
            pt7 = [pt0[0] + abs((pt1[0]-pt0[0])*2/3), pt0[1] - abs((pt1[1]-pt0[1])*4/7)]
        else:
            pt7 = [pt0[0] - abs((pt1[0]-pt0[0])*2/3), pt0[1] - abs((pt1[1]-pt0[1])*4/7)]

        pt8 = [pt7[0] + blackTW, pt7[1] + blackTH]
        pt9 = [pt0[0] + blackBW, pt0[1] + blackBH]

        # Select points required to build key
        if keyNum == 1:
            key = [pt0, pt1, pt2, pt3]

        elif keyNum == 2 or keyNum == 6:
            key = [pt0, pt1, pt2, pt4, pt5, pt6]

            black_key.append(pt5)
            black_key.append(pt6)

        elif keyNum == 5 or keyNum == 8:
            key = [pt1, pt2, pt3, pt9, pt8, pt7]

            black_key.append(pt9)
            black_key.append(pt8)
            keys.append(black_key)
            black_key = [] 

        else:   #3, 4, 7
            key = [pt1, pt2, pt4, pt5, pt6, pt9, pt8, pt7]

            black_key.append(pt9)
            black_key.append(pt8)
            keys.append(black_key)
            black_key = []
            black_key.append(pt5)
            black_key.append(pt6)
        #key = [pt0, pt1, pt2, pt3]

        print keyNum
        print key
        keys.append(key)
        keyNum += 1

    # Turn everything into ints after, so no truncation
    int_keys = []
    for key in keys:
        int_key = []
        for point in key:
            int_point = [int(point[0]), int(point[1])]
            int_key.append(int_point)
        int_keys.append(int_key)

    return int_keys

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
     
    # allow the camera to warmup
    time.sleep(0.1)

    #CREATE TRACKBARS TO CONTROL HSV

    def nothing(x):
        pass
    # Creating a window for later use
    cv2.namedWindow('result')

    # MADDY'S CHANGES START HERE...
    #gets all points in notes and puts them in a single point array
    pts = setup.mapToCameraView(camera)

    notes = calculate_key_points(pts)

    allNotePoints = []
    for note in notes:
        for x, y in note:
            coord = (x, y)
            allNotePoints.append(coord)

    orig = cv2.imread('images/testBlack2.jpg')
    for note in notes:
        cv2.polylines(orig, [np.int32(note)],1,teal)
    #cv2.imshow("original++", orig)
        
    # Project the keyboard
    keyboard = piano_projection.projectImage('images/8-keys-black.jpg')
    cv2.imshow("keyboard", keyboard)
    cv2.moveWindow("keyboard", -30, 200)

    # Starting with 100's to prevent error while masking
    rawCapture = PiRGBArray(camera, size=(640, 480))
    lowerRange=HSVAutoCalib2.calib(camera,rawCapture,laserLinePin)

    h=lowerRange[0]
    s=lowerRange[1]
    v=lowerRange[2]

    # Creating track bar Prev: 142,64,161
    # the first integer parameter are the starting values

    cv2.createTrackbar('h', 'result',h,179,nothing)
    cv2.createTrackbar('s', 'result',s,255,nothing)
    cv2.createTrackbar('v', 'result',v,255,nothing)

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

    #Initialize the array of notes (top to bottom of keyboard)
    notesList = []
    notesList.append(pygame.mixer.Sound("pianoSounds/C4.wav"))
    notesList.append(pygame.mixer.Sound("pianoSounds/B4.wav"))
    notesList.append(pygame.mixer.Sound("pianoSounds/A#4.wav"))
    notesList.append(pygame.mixer.Sound("pianoSounds/A4.wav"))
    notesList.append(pygame.mixer.Sound("pianoSounds/G#4.wav"))
    notesList.append(pygame.mixer.Sound("pianoSounds/G4.wav"))
    notesList.append(pygame.mixer.Sound("pianoSounds/F#4.wav"))
    notesList.append(pygame.mixer.Sound("pianoSounds/F4.wav"))
    notesList.append(pygame.mixer.Sound("pianoSounds/E4.wav"))
    notesList.append(pygame.mixer.Sound("pianoSounds/D#4.wav"))
    notesList.append(pygame.mixer.Sound("pianoSounds/D4.wav"))
    notesList.append(pygame.mixer.Sound("pianoSounds/C#4.wav"))
    notesList.append(pygame.mixer.Sound("pianoSounds/C4.wav"))



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

        print "KEYPOINTS:"
        print keypoints

        
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
            cv2.moveWindow('piano', 0, 0)
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

if __name__ == "__main__":
    main()
