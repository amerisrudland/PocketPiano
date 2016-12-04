Features implemented:
-Live threshold modification
-Blob detection (i.e finger detection)
-Sound played in response to finger detection

Next Steps:
"I've uploaded a lot of mini-programs onto the Git which show how to implement various functions.
The MainCode file is the most up to date implementation of the project, which encompasses many of the functions
demonstrated in the mini-programs. The current version of the MainCode is able to detect fingers by using
a blobDetection class. The parameters in the blobDetection class are used to find the blobs in the masked
image. In addition to drawing red circles around these blobs (on the un-masked image), the centre of each blob
is stored in a keypoints array. 

Currently, it plays a sound when a single note is played (i.e the keypoints array is NOT empty). The next
step is to differentiate different locations on screen. I have thought of two ways this can be implemented:

1. Coordinate comparison.
The coordinates of the keypoints are all accessible. For example
x=keypoints[2].pt[0]
y=keypoints[2].pt[1]
gets the x and y coordinates of the third keypoint. You can iterate through all keypoints then check if their
locations are within certain bounds (the bounds defining areas of the screen)

I do not recommend this approach because it can be difficult to tell if the keypoint is in a non-rectangular shape.

2. Multiple masks
This method expands on the current implementation of how the detector is used. Currently, the keypoints array is built
with the line of code:
keypoints = detector.detect(blurredMask).
Which checks the blurredMask for white blobs, and makes keypoints for each blob. According to documentation, the detect
function can be expanded on to only search the image in a specific area, as defined by a mask. So the new code might look
something like:
keypoints = detector.detect(blurredMask,searchAreaMask).
I have created a DrawShapes.py file which shows how to create custom masks. Ideally we can create customized masks for
different regions of space and the code would look like:
blobInRegionA = detector.detect(blurredMask,regionA)
blobInRegionB = detector.detect(blurredMask,regionB)
blobInRegionC = detector.detect(blurredMask,regionC)

then a check of

if blobInRegionA: #array not empty
   print 'region A detected'
etc...

It should be obvious that we would eventually expand the program to create masks based on the piano keyboard, and thus
the regions would correspond to specific notes. Then, instead of printing, the sounds would be played.

I THINK this isn't computer intensive, because the detector is only being called to search small areas.

3. Other method
These are two methods of thought of based on what I know about openCV, but there may be other, more efficient
ways to implement the code.

Anyways, good luck. I've commented MainLoop pretty thoroughly so you shouldn't have any trouble understanding what's going on."

-Jeff