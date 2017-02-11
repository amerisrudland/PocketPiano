""" Project an image of a keyboard through the
mini-projector. Manipulate the image such that
it is resized and rotated correctly. """

import numpy as np
import cv2
import time

####################################################################
def projectImage(image_path):
	""" Read in image and manipulate it to display correctly. """
	
	# Read image and shrink it
	img = cv2.imread(image_path)
	rows,cols,ch = img.shape
	pts1 = np.float32([[0,0],[0, rows],[cols,0],[cols,rows]])	#Original
	pts2 = np.float32([[0,0],[0, rows/2],[cols,0],[cols,rows/2]])	#Shrink
	M = cv2.getPerspectiveTransform(pts1,pts2)
	shrink = cv2.warpPerspective(img,M,(cols, rows/2))

	# Take shrunk image and transform into trapezoid
	rows,cols,ch = shrink.shape
	pts3 = np.float32([[cols/8, 0],[0, rows],[cols - cols/8, 0],[cols, rows]])	#Trapizoid
	M = cv2.getPerspectiveTransform(pts2,pts3)
	trap = cv2.warpPerspective(shrink,M,(cols, rows))

	# Take trapezoid and translate
	rows,cols,ch = trap.shape
	M = np.float32([[1, 0, 0], [0, 1, rows/3]])
	translate = cv2.warpAffine(trap,M,(cols, rows))

	# Resize image
	rows, cols, ch = translate.shape
	final = cv2.resize(translate, None, fx=1.25, fy=1.25, interpolation = cv2.INTER_CUBIC)	
	return final
	
####################################################################
def displayImage(image_path, winName, x, y, delay):
	""" Display an image at the given coordinates for the given duration. 
	image_path 	= image name (string)
	winName		= name of window image is shown in (string)
	x			= x coordinate of window (int)
	y 			= y coordinate of window (int)
	delay		= time in ms to display window (int) """
	
	image = projectImage(image_path)
	cv2.imshow(winName, image)
	cv2.moveWindow(winName, x, y)
	cv2.waitKey(delay)
	cv2.destroyWindow(winName)
	
####################################################################
def main():
	# Project blank keyboard
	displayImage("images/8-keys-white.jpg", "White", 175, 325, 1000)

	# Project true keyboard
	displayImage("images/8-keys-black.jpg", "Keyboard", 175, 325, 1000)
	
####################################################################
if __name__ == "__main__":
    main()
