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
def main():
	# Project blank keyboard
	white = projectImage("8-keys-white.jpg")
	cv2.imshow("White", white)
	cv2.moveWindow("White", 175, 325)
	cv2.waitKey(1000)
	cv2.destroyWindow("White")

	# Project true keyboard
	keys = projectImage("8-keys-black.jpg")
	cv2.imshow("Keyboard", keys)
	cv2.moveWindow("Keyboard", 175, 325)
	cv2.waitKey(1000)
		
	cv2.destroyAllWindows()
	
####################################################################
if __name__ == "__main__":
    main()