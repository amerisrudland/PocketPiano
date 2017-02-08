import cv2

image = cv2.imread('test.png')
cv2.imshow('test',image)

#The code loads an image (test.png). When the user has the image selected,
#the console will respond to keys being pressed
#http://www.asciitable.com/
while True:
    k = cv2.waitKey(5) & 0xFF #waits 5 miliseconds, checking for any keyboard input (returns the ascii value of the key pressed)
    if k == 27: #ascii value for ESC
        break
    if k == 119: #ascii for w
        print 'w'
    if k == 115: #ascii for s
        print 's'
    if k == 97: #ascii for a
        print 'a'
    if k == 100: #ascii for d
        print 'd'
    if k == 101: #ascii for e
        print 'e'
    if k == 113: #ascii for q
        print 'q'
