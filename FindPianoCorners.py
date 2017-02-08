"""
2017-02-07
This program finds the corners of the projected piano image.
It takes 2 images, manipulates and subtracts them to find
the keyboard. Then it finds the edges of the remaining image
and creates a skewed rectangle around these edges. From the
skewed rectangle the coordinates of the piano's corners can 
be found. 
""" 

import cv2
import numpy as np

TEAL = (161,232,9)
	
####################################################################
def translateAndCrop(image, t_x, t_y):
	""" Translate the image by t_x and t_y,
	then crop the frame by 3/5 in x and 1/3 in y.
	Note that the frame cropping dimensions could
	not be made dynamic for some reason. """
	
	rows, cols, ch = image.shape	# Get size of original image
	translate = np.float32([[1, 0, t_x], [0, 1, t_y]])	
	changed_image = cv2.warpAffine(image, translate, (cols*3/5, rows/3))
	return changed_image
	
####################################################################
def findKeyboard(key_image, white_image):
	""" Read image with keyboard and image with white 
	where keyboard should be. Manipulate images to find
	keyboard area and subtract images to display only
	the keyboard. The same operations should be applied 
	to both images, such that the mapping is preserved"""
	
	piano_keys = cv2.imread(key_image)
	mask = cv2.imread(white_image)
	cut_piano_keys = translateAndCrop(piano_keys, -150, -650)
	cut_mask = translateAndCrop(mask, -150, -650)
	result = cv2.subtract(cut_mask, cut_piano_keys)
	return result

####################################################################
def findEdgeCoordinates(image):
	""" Find edges in an image and gather the coordinates of the 
	points along all of them. """
	# Find the edges of the keyboard
	edges = cv2.Canny(image, 0, 80)	# Parameters: image, lower threshold, upper threshold
	edge_coords = []
	for y in range(0, edges.shape[0]):
		for x in range(0, edges.shape[1]):
			if edges[y,x] != 0:		# The pixel isn't black
				coord = [x, y]
				edge_coords.append(coord)
	return edge_coords

####################################################################
def pianoCoordinates(edge_coordinates):
	""" Create a skewed rectangle surrounding edges. This box will 
	find the bottom 2 corners of the piano (box[0] and box[3]) The 
	other 2 corners of this box (box[1] and bpx[2]) can be used to 
	find the remaining piano coordinates. """
	# Create rectangle using points along edges
	rect = cv2.minAreaRect(np.array(edge_coordinates))
	box = cv2.boxPoints(rect)	# Gather coordinates of box corners
	box = np.int0(box)
	
	bottom_left = [box[0][0], box[0][1]]
	bottom_right = [box[3][0], box[3][1]]

	# Use the box to calculate the upper 2 corners of the actual piano
	# Find top left corner
	x = box[0][0] + ((box[0][1] - box[1][1])*2/3) #194 + ((258 - 69)*2/3)
	y = box[1][1] + ((box[1][0] - box[0][0])*2/3) #69 + ((180 - 194)*2/3)
	top_left = [x, y]

	# Find top right corner
	x = box[2][0]-((box[3][1]-box[2][1])*1/3)
	y = box[2][1]+((box[3][0]-box[2][0])*2/3)
	top_right = [x, y]

	piano_coords = [bottom_left, top_left, top_right, bottom_right]
	return piano_coords

####################################################################
def markCoordinates(image, coordinates, colour, weight=2):
	""" Draw cross-hairs "+" and label coordinates on image. """
	for x,y in coordinates:
		#Draw cross-hairs
		cv2.line(image, (x,y-3), (x,y+3), colour, weight)
		cv2.line(image, (x-3,y), (x+3,y), colour, weight)
		#label coordinates
		cv2.putText(image, '{0},{1}'.format(x,y),(x+30,y+20),cv2.FONT_HERSHEY_DUPLEX,0.5,(255, 255, 255),1)
		
####################################################################
def outlineShape(image, coordinates, colour, weight=2):
	""" Draw lines to form enclosed shape from coordinates. """
	for idx in range(0, len(coordinates)):
		if idx == len(coordinates) - 1:	# Connect start and end points
			cv2.line(image, (int(coordinates[idx][0]), int(coordinates[idx][1])), (int(coordinates[0][0]), int(coordinates[0][1])), colour, weight)
		else:
			cv2.line(image, (int(coordinates[idx][0]), int(coordinates[idx][1])), (int(coordinates[idx+1][0]), int(coordinates[idx+1][1])), colour, weight)
			
####################################################################
def main():

	# manipulate 2 images to find the keyboard and only the keyboard
	result = findKeyboard('key_test_black.jpg', 'key_test_white2.jpg')
	
	# Gather the coordinates of the points along all edges
	edge_coords = findEdgeCoordinates(result)

	# Find the coordinates of the piano from the edges 
	piano_coords = pianoCoordinates(edge_coords)
	print piano_coords
	
	# Display coordinates/cross-hairs of trapezoid defining piano
	markCoordinates(result, piano_coords, TEAL)
		
	# Connect the trapezoid defining piano
	outlineShape(result, piano_coords, TEAL)
	
	cv2.imshow('result', result)
	cv2.waitKey(0)
	cv2.destroyAllWindows()

####################################################################
if __name__ == "__main__":
    main()