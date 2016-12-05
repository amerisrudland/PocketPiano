import cv2
import numpy as np

#lots more shapes in documentation
#Documentation:http://docs.opencv.org/2.4/modules/core/doc/drawing_functions.html

#IMPORTANT: This method of creating shapes can be used to create customized masks!

#create all black image
image=np.zeros((800,800,3),npuint8)
#define the color (white)
color = (255,255,255)

#Note: a thickness of -1 fills the shape

#Drawing a Line
#cv2.line(img, pt1, pt2, color[, thickness[, lineType[, shift]]])
cv2.line(image,(200,100),(250,150), color, 4)
 
#Drawing a Rectangle
#cv2.rectangle(img, pt1, pt2, color[, thickness[, lineType[, shift]]])
cv2.rectangle(image, (300,100) , (500,300),color,-1)
 
#Drawing a Circle
#cv2.circle(img, center, radius, color[, thickness[, lineType[, shift]]]) 
cv2.circle(image,(100,100),50,color,-1,8);



#drawing polyLines
#cv2.polylines(img, pts, isClosed, color[, thickness[, lineType[, shift]]])
points=np.int32([(600,100),(610,120),(625,110),(650,140)])
cv2.polylines(image, [points], 1, color)

#Drawing a polygon
#cv2.fillPoly(img, pts, color[, lineType[, shift[, offset]]])
points=np.int32([(700,100),(710,120),(725,110),(750,140)])
cv2.fillPoly(image, [points],color)

#Adding text
#cv2.putText(img, text, org, fontFace, fontScale, color[, thickness[, lineType[, bottomLeftOrigin]]])
cv2.putText(image, 'this text brought to you by Jeffrey!', (50,400),cv2.FONT_HERSHEY_DUPLEX,1.5,color,1)


cv2.imshow('Image',image)
k = cv2.waitKey(0)

