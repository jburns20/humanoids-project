from __future__ import print_function
import numpy as np
import imutils  # not neccesary but remove line 174
import cv2
import math

def draw_flow(img, flow, step=8):
    h, w = img.shape[:2]
    y, x = np.mgrid[step/2:h:step, step/2:w:step].reshape(2,-1)

    fx, fy = flow[y,x].T
    lines = np.vstack([x, y, x+fx, y+fy]).T.reshape(-1, 2, 2)
    lines = np.int32(lines + 0.5)
    vis = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    cv2.polylines(vis, lines, 0, (0, 255, 0))
    for (x1, y1), (x2, y2) in lines:
        cv2.circle(vis, (x1, y1), 1, (0, 255, 0), -1)
    return vis



def getArea(rect, mask, img, maxRadius):

    contours = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)[-2]
    maxContour = max(contours, key=cv2.contourArea)

    hull = cv2.convexHull(maxContour)
    moments = cv2.moments(maxContour)
    if moments['m00'] != 0:
                cx = int(moments['m10']/moments['m00'])  # cx = M10/M00
                cy = int(moments['m01']/moments['m00'])  # cy = M01/M00

    centr = (cx, cy)          
    cv2.circle(img, centr, 5, [0, 0, 255], 2)
    cv2.drawContours(img, [maxContour], 0, (0, 255, 0), 2)
    cv2.drawContours(img, [hull], 0, (0, 0, 255), 2)
    # peri = cv2.arcLength(maxContour, True)
    # approx = cv2.approxPolyDP(maxContour, 0.02 * peri, True)
    rectArea = rect[1][0]*rect[1][1]
    contourArea = cv2.contourArea(maxContour)  # or approx
    return (rectArea, contourArea)


def hsv_to_rgb(h, s, v):
    h = float(h)
    s = float(s)
    v = float(v)
    h60 = h / 60.0
    h60f = math.floor(h60)
    hi = int(h60f) % 6
    f = h60 - h60f
    p = v * (1 - s)
    q = v * (1 - f * s)
    t = v * (1 - (1 - f) * s)
    r, g, b = 0, 0, 0
    if hi == 0:
        r, g, b = v, t, p
    elif hi == 1:
        r, g, b = q, v, p
    elif hi == 2:
        r, g, b = p, v, t
    elif hi == 3:
        r, g, b = p, q, v
    elif hi == 4:
        r, g, b = t, p, v
    elif hi == 5:
        r, g, b = v, p, q
    r, g, b = int(r * 255), int(g * 255), int(b * 255)
    return (r, g, b)


def createMask(img, lowerbound, upperbound):
    # convert image into HSV.
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    # construct a mask to isolate the yellow glove from the screen
    mask = cv2.inRange(hsv, lowerbound, upperbound)
    mask = cv2.erode(mask, None, iterations=3)
    mask = cv2.dilate(mask, None, iterations=3)
    return mask


def main():
    # ####upper and lower bounds for colors
    # yellow bounds from:
    # https://stackoverflow.com/questions/9179189/detect-yellow-color-in-opencv
    prevgray = None
    flow = None
    camera = cv2.VideoCapture(0)
    lower_blue = np.array([64, 174, 145])
    upper_blue = np.array([141, 255, 255])
    lower_yellow = np.array([158 , 100, 100])
    upper_yellow = np.array([178, 255, 255])
    lower_red = np.array([170, 50, 50])
    upper_red = np.array([200, 255, 255])
    lower_orange = np.array([5, 50, 50])
    upper_orange = np.array([15, 255, 255])
    count = 0
    ret, prev = camera.read()
    firstprev = prev
    firstprevgray = cv2.cvtColor(firstprev, cv2.COLOR_BGR2GRAY)
    staticBox = 0

    while True:
        (ret, img_frame) = camera.read()

        img_frame = imutils.resize(img_frame, width=900)
        img_frame = cv2.flip(img_frame, 1)

        # create mask to block out all colors but blue
        mask = createMask(img_frame, lower_blue, upper_blue)
        cv2.imshow("asdf",mask)
        # create gray copy to isolate face
        gray = img_frame.copy()
        gray = cv2.cvtColor(gray, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)
        gray2 = cv2.cvtColor(img_frame, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.bilateralFilter(gray2, 11, 17, 17)
        edged = cv2.Canny(gray2, 30, 200)
        cv2.imshow("edge", edged)


        # find contours in the mask and initialize the current cnter of contour
        contours = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                                    cv2.CHAIN_APPROX_SIMPLE)[-2]
        cnts = sorted(contours, key = cv2.contourArea, reverse = True)[:2]

        center = None

        # only proceed if at least one contour was found
        if len(cnts) > 1:
            # find the largest contour in the mask
            maxContour = cnts[0]

            # creates the smallest bounding circle about the contour
            ((x, y), radius) = cv2.minEnclosingCircle(cnts[0])
            if len(cnts)>1:
                ((x1, y1), radius2) = cv2.minEnclosingCircle(cnts[1])
            # cv2.rectangle(img_frame,(int(x),int(y)),(int(x1),int(y1)),(0,255,0),3)
            
            bottomRight = (int(max(x,x1)),int(max(y,y1)));
            topleft = (int(min(x,x1)),int(min(y,y1)));
            cv2.circle(img_frame, bottomRight, 1, [0, 0, 255], 2)
            cv2.circle(img_frame, topleft, 1, [0, 0, 255], 2)

            print ("%d" %((((topleft[0]-bottomRight[0])**2)+ ((topleft[1]-bottomRight[1])**2))**.5))
            print("here")


            if ((200> ((((topleft[0]-bottomRight[0])**2) +((topleft[1]-bottomRight[1])**2))**.5)>50)):
                print ("in here")
                staticBox = [(bottomRight[0]-200,bottomRight[1]-200), bottomRight]
            if (staticBox != 0):
                cv2.circle(img_frame, bottomRight, 1, [0, 0, 255], 2)
                # cv2.rectangle(img_frame, (int(x), int(y)), (int(x1), int(y1)), [255,0,0], thickness=1, lineType=8, shift=0)
                cv2.rectangle(img_frame, staticBox[0], staticBox[1], [255,0,0], thickness=1, lineType=8, shift=0)
                img = img_frame[staticBox[0][1]:staticBox[1][1], staticBox[0][0]:staticBox[1][0]]
                print("%(a)d %(b)d %(c)d %(d)d" % {"a":staticBox[0][0], "b":staticBox[0][1], "c":staticBox[1][0], "d":staticBox[1][1]})
                print("HELLo ") 
                if (count <1):
                    prevgray = firstprevgray[staticBox[0][1]:staticBox[1][1], staticBox[0][0]:staticBox[1][0]]

                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

                flow = cv2.calcOpticalFlowFarneback(prevgray, gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)
                
                prevgray = gray
                count+= 1



            # centr = (cx, cy)
            # cv2.circle(img_frame, centr, 1, [0, 0, 255], 2)
            # cv2.drawContours(img_frame, [maxContour], 0, (0, 255, 0), 2)
            # cv2.drawContours(img_frame, [hull], 0, (0, 0, 255), 2)

            # rectArea = rect[1][0]*rect[1][1]
            # contourArea = cv2.contourArea(maxContour)  # or approx
            # widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
            # widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
             
            # # ...and now for the height of our new image
            # heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
            # heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
             
            # # take the maximum of the width and height values to reach
            # # our final dimensions
            # maxWidth = max(int(widthA), int(widthB))
            # maxHeight = max(int(heightA), int(heightB))
 
            # # construct our destination points which will be used to
            # # map the screen to a top-down, "birds eye" view
            # dst = np.array([
            #     [0, 0],
            #     [maxWidth - 1, 0],
            #     [maxWidth - 1, maxHeight - 1],
            #     [0, maxHeight - 1]], dtype = "float32")
            #             # taken from openCv website

            # M = cv2.moments(maxContour)
            # center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
            # # draw the circle and centroid on the img_frame,
            # # then update the list of tracked points
            # cv2.circle(img_frame, (int(x), int(y)), int(radius),
            #            (0, 255, 255), 2)
            # cv2.circle(img_frame, center, 15, (230, 12, 45), -1)
            # areaString = "%(rect)d | %(cont)d " \
            #     % {"rect": rectArea, "cont": contourArea}
            # cv2.putText(img_frame, areaString, (20, 80),
            #             cv2.FONT_HERSHEY_SIMPLEX, 2, 255)

        if (flow != None):
            cv2.imshow('Frame', draw_flow(img, flow))
        else:
            cv2.imshow("Frame", img_frame)
        key = cv2.waitKey(1) & 0xFF

        # if the 'q' key is pressed, stop the loop
        if key == ord("q"):
            break
    # cleanup the camera and close any open windows
    camera.release()
    cv2.destroyAllWindows()
main()
