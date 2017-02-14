import cv2
from picamera import PiCamera
import piano_projection
import FindPianoCorners
import time

TEAL = (161,232,9)
BLACK = (0, 0, 0)

####################################################################
def mapToCameraView(camera):
        ''' Get the coordinates of the piano's corners as seen by the camera. '''
        
        # find the keyboard
        piano = getPiano(camera)
	
	# Gather the coordinates of the points along all edges
	edge_coords = FindPianoCorners.findEdgeCoordinates(piano)

	# Find the coordinates of the piano from the edges 
	piano_coords = FindPianoCorners.pianoCoordinates(edge_coords)

	# Map coordinates back to camera's view (undo translations)
	piano_coords_cam = []
	for x, y in piano_coords:
		x_cam = x - FindPianoCorners.T_X
		y_cam = y - FindPianoCorners.T_Y
		cam_coord = (x_cam, y_cam)
		piano_coords_cam.append(cam_coord)

	return piano_coords_cam

####################################################################
def getPiano(camera):
        ''' Project 2 images and subtract them to find the keyboard. '''
        
        # Project blank image and take picture
	piano_projection.displayImage('images/8-keys-white.jpg', 'white', -30, 200, 1000)
	camera.capture('images/testWhite2.jpg')

	# Project image of piano and take picture
	piano_projection.displayImage('images/8-keys-black.jpg', 'keys', -30, 200, 1000)
	camera.capture('images/testBlack2.jpg')

	# manipulate 2 images to find the keyboard and only the keyboard
	piano = FindPianoCorners.findPiano('images/testBlack2.jpg', 'images/testWhite2.jpg')
        return piano

####################################################################
def showCorners(winName, image, coords):
        ''' Display coordinates/cross-hairs and connect lines.
        winName - the window the image will appear in (string)
        image   - the actual image (ouput of cv2.imread(<path>)
        coords  - the coordinates to be placed on the image (list). '''
        
	FindPianoCorners.markCoordinates(image, coords, TEAL)
	FindPianoCorners.outlineShape(image, coords, TEAL)
	cv2.imshow(winName, image)

####################################################################
def main():
        # Set up camera
	camera = PiCamera()
    	camera.resolution = (640, 480)
    	camera.framerate = 32
     
	# allow the camera to warmup
	time.sleep(0.1)

        # Get corner points and display them
	pts = mapToCameraView(camera)
	print pts
	keys = cv2.imread('images/testBlack2.jpg')
	showCorners('Keyboard Corners', keys, pts)

	cv2.waitKey(0)
	cv2.destroyAllWindows()
	
####################################################################
if __name__ == "__main__":
    main()
