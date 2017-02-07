import cv2
import numpy as np

frame = cv2.imread('key_test_black.jpg')
hsv= cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
#creates a mask with a lower threshold using the hsv values
#and upper threshold of 180,255,255
lowerRange = np.array([0,0,180])
upperRange = np.array([0,0,210]) 
mask = cv2.imread('key_test_white2.jpg')
#mask = cv2.inRange(frame, lowerRange, upperRange)
cv2.imshow('Original', frame)
#The blurred image to reduce noise (higher number = more blurred; Must be odd number)
#mask = cv2.medianBlur(mask,7)

#Cut images in half to have get just area around piano
rows, cols, ch = frame.shape
M = np.float32([[1, 0, -150], [0, 1, -650]])
cut_frame = cv2.warpAffine(frame, M, (cols*3/5, rows/3))#(437-88, 375-270))
rows, cols, ch = mask.shape
cut_mask = cv2.warpAffine(mask, M, (cols*3/5, rows/3))#(437-88, 375-270))

cv2.imshow("frame cut", cut_frame)
cv2.imshow("mask cut", cut_mask)


# Bitwise-AND mask and original image
result = cv2.subtract(cut_mask, cut_frame) #cv2.bitwise_and(frame,frame, mask= mask)
#cv2.imshow('result',result)

#cv2.imshow('frame', frame)

edges = cv2.Canny(result, 0, 70)
cv2.imshow('edges', edges)

edge_coords = []
for y in range(0, edges.shape[0]):
    for x in range(0, edges.shape[1]):
        if edges[y,x] != 0:
            coord = [x, y]
            edge_coords.append(coord)

#USEFUL SHIT????

pianoX,pianoY,pianoWidth,pianoHeight = cv2.boundingRect(np.array(edge_coords))
cv2.rectangle(result, (pianoX,pianoY),(pianoX+pianoWidth,pianoY+pianoHeight), (0, 255, 0), 2)

rect = cv2.minAreaRect(np.array(edge_coords))
box = cv2.boxPoints(rect)
box = np.int0(box)
cv2.drawContours(result, [box], 0, (0, 0, 255), 2)

#WHAT THE SHIT IS GOING ON AFTER THIS???@??@??@?
##grey_result = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)
##ret, thresh = cv2.threshold(grey_result, 127, 255, 0)
##im2, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
##contour = contours[0]
##print contours
###moment = cv2.moments(contour)
##epsilon = 0.1*cv2.arcLength(contour, True)
##approx = cv2.approxPolyDP(contour, epsilon, True)
##print approx
##cv2.drawContours(result, [approx], 0, (255, 0, 0), 2)
###perimeter = cv2.contourArea(np.array(edge_coords))
##print box

# USELESS SHIT....
##edges_xfirst = []
##edges_yfirst = []
##
##
##for y in range(0, edges.shape[0]):
##    for x in range(0, edges.shape[1]):
##        if edges[y,x] != 0:
##            coords_xfirst = [x, y]
##            coords_yfirst = [y, x]
##            edges_xfirst.append(coords_xfirst)
##            edges_yfirst.append(coords_yfirst)
##
###print edge_coords
##edges_xfirst.sort()
##edges_yfirst.sort()
##print edges_xfirst
##print "\n"
##print edges_yfirst
##
##end_x = 0
##end_y = 0
##
##corners = []
##start = [edges_xfirst[0][0], edges_xfirst[0][1]]
##corners.append(start)
##
##idx = 0
##x = edges_xfirst[idx][0]
##y = edges_xfirst[idx][1]
##
##
##while (x >= end_x and y >= end_y):
##    end_x = x
##    end_y = y
##
##    idx += 1
##    x = edges_xfirst[idx][0]
##    y = edges_xfirst[idx][1]
##
##endpt = [end_x, end_y]
##corners.append(endpt)
##print endpt
##
##pt = [edges_yfirst[-1][1], edges_yfirst[-1][0]]
##print pt
##corners.append(pt)
##corners.append(edges_xfirst[-1])
##
##print corners


teal = (161,232,9)

#print "The first coordinate has an x of {0} and a y of {1}".format(edge_coords[0][0], edge_coords[0][1])

#cv2.line(result, (int(edges_xfirst[0][0]), int(edges_xfirst[0][1])), (int(edges_xfirst[-1][0]), int(edges_xfirst[-1][1])), teal, 1)
#cv2.line(result, (int(edges_yfirst[0][1]), int(edges_yfirst[0][0])), (int(edges_yfirst[-1][1]), int(edges_yfirst[-1][0])), teal, 1)

#for idx in range(0, len(corners)-1):
#    cv2.line(result, (int(corners[idx][0]), int(corners[idx][1])), (int(corners[idx+1][0]), int(corners[idx+1][1])), teal, 1)
    
cv2.imshow('edges', edges)
cv2.imshow('result', result)
cv2.waitKey(0)
cv2.destroyAllWindows()
