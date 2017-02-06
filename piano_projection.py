import numpy as np
import cv2
img = cv2.imread("8-keys.jpg")
#cv2.imshow("Original", img)
#cv2.waitKey(0)

rows,cols,ch = img.shape

print rows
print cols
print ch

pts1 = np.float32([[0,0],[0, rows],[cols,0],[cols,rows]])	#Original
pts2 = np.float32([[0,0],[0, rows/2],[cols,0],[cols,rows/2]])	#Shrink
M = cv2.getPerspectiveTransform(pts1,pts2)
shrink = cv2.warpPerspective(img,M,(cols, rows/2))

#cv2.imshow("Shrink", shrink)

rows,cols,ch = shrink.shape
pts3 = np.float32([[cols/8, 0],[0, rows],[cols - cols/8, 0],[cols, rows]])	#Trapizoid
M = cv2.getPerspectiveTransform(pts2,pts3)
trap = cv2.warpPerspective(shrink,M,(cols, rows))

#cv2.imshow("Trapizoid", trap)	# Good widths, straight, white keys too long.

rows,cols,ch = trap.shape
#pts4 = np.float32([[cols/16, rows/2],[0, rows],[cols - cols/16, rows/2],[cols, rows]])	#Trapizoid
#pts5 = np.float32([[cols/8, 0],[cols/16, rows/2],[cols - cols/8, 0],[cols - cols/16, rows/2]])	#Trapizoid
M = np.float32([[1, 0, 0], [0, 1, rows/3]])
small = cv2.warpAffine(trap,M,(cols, rows))

rows, cols, ch = small.shape
dst = cv2.resize(small, None, fx=1.25, fy=1.25, interpolation = cv2.INTER_CUBIC)

cv2.imshow("Warped", dst)
cv2.waitKey(0)

#plt.subplot(121),plt.imshow(img),plt.title('Input')
#plt.subplot(122),plt.imshow(dst),plt.title('Output')
#plt.show()