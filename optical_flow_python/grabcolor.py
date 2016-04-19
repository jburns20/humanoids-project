import cv2
import numpy as np
import imutils  # not neccesary but remove line 174


cap = cv2.VideoCapture(0)

def nothing(x):
    pass
# Creating a window for later use
cv2.namedWindow('result')


def createMask(img, lowerbound, upperbound):
    # convert image into HSV.
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    # construct a mask to isolate the yellow glove from the screen
    mask = cv2.inRange(hsv, lowerbound, upperbound)
    mask = cv2.erode(mask, None, iterations=1)
    mask = cv2.dilate(mask, None, iterations=1)
    return mask



# Starting with 100's to prevent error while masking
h,s,v = 100,100,100

# Creating track bar
cv2.createTrackbar('h', 'result',0,179,nothing)
cv2.createTrackbar('s', 'result',0,255,nothing)
cv2.createTrackbar('v', 'result',0,255,nothing)
cv2.createTrackbar('h1', 'result',0,179,nothing)
cv2.createTrackbar('s1', 'result',0,255,nothing)
cv2.createTrackbar('v1', 'result',0,255,nothing)

while(1):

    _, frame = cap.read()
    frame = imutils.resize(frame, width=600)


    #converting to HSV
    hsv = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)

    # get info from track bar and appy to result
    h = cv2.getTrackbarPos('h','result')
    s = cv2.getTrackbarPos('s','result')
    v = cv2.getTrackbarPos('v','result')
    h1 = cv2.getTrackbarPos('h1','result')
    s1 = cv2.getTrackbarPos('s1','result')
    v1 = cv2.getTrackbarPos('v1','result')

    # Normal masking algorithm
    lower_blue = np.array([h,s,v])
    upper_blue = np.array([180,255,255])

    mask = cv2.inRange(hsv,lower_blue, upper_blue)

    result = cv2.bitwise_and(frame,frame,mask = mask)
    test = "h: %(hue)d" % {"hue": h}
    cv2.putText(result,test, (100,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255))
    test = "s: %(sat)d" % {"sat": s}
    cv2.putText(result,test, (100,100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255))
    test = "v: %(val)d" % {"val": v}
    cv2.putText(result,test, (100,150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255))
    cv2.imshow('result',result)
    mask = createMask(frame, np.array([h, s, v]), np.array([h1, s1, v1]))
    cv2.imshow("asdf",mask)

   
    k = cv2.waitKey(5) & 0xFF
    if k == 27:
        break

cap.release()

cv2.destroyAllWindows()
