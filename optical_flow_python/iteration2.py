
'''Second iteration of background subtraciton for Humanoids Comupter Vision'''

from __future__ import print_function
import numpy as np
import imutils  # not neccesary but remove line 174
import cv2
import math
from threading import Thread
class WebcamVideoStream:
    def __init__(self, src=0):
        # initialize the video camera stream and read the first frame
        # from the stream
        self.stream = cv2.VideoCapture(src)
        (self.grabbed, self.frame) = self.stream.read()
 
        # initialize the variable used to indicate if the thread should
        # be stopped
        self.stopped = False
    def start(self):
        # start the thread to read frames from the video stream
        Thread(target=self.update, args=()).start()
        return self
 
    def update(self):
        # keep looping infinitely until the thread is stopped
        while True:
            # if the thread indicator variable is set, stop the thread
            if self.stopped:
                return
 
            # otherwise, read the next frame from the stream
            (self.grabbed, self.frame) = self.stream.read()
 
    def read(self):
        # return the frame most recently read
        return self.frame
 
    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True


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
    camera = cv2.VideoCapture(0)
    vs = WebcamVideoStream(src=0).start()

    lower_blue = np.array([110, 50, 50])
    upper_blue = np.array([130, 255, 255])
    lower_yellow = np.array([20, 100, 100])
    upper_yellow = np.array([30, 255, 255])
    grabBackground = 0;
    fgbg = None;
    reduction =None
    background = None
    grabbed = False
    while True:
        img_frame = vs.read()
        # set up img_frame for masking
        img_frame = imutils.resize(img_frame, width=900)
        img_frame = cv2.flip(img_frame, 1)
        blah = img_frame.copy()
        if (grabBackground <30):
            grabBackground += 1
        elif not grabbed:
            fgbg = cv2.createBackgroundSubtractorKNN()
            background = img_frame.copy()
            grabbed = True

        # create mask to block out all colors but blue
        if fgbg != None:
            img_frame = fgbg.apply(img_frame)
        if background != None:
            res = cv2.subtract(background,blah)

        else: res = img_frame.copy()
        res = cv2.erode(res, None, iterations=1)
        res = cv2.dilate(res, None, iterations=1) 
        img_frame = cv2.erode(img_frame, None, iterations=2)
        img_frame = cv2.dilate(img_frame, None, iterations=2)  
        if grabbed:
            contours = cv2.findContours(img_frame.copy(), cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_SIMPLE)[-2]
            center = None

        # only proceed if at least one contour was found
        if grabbed and (len(contours) > 0):
            # find the largest contour in the mask, then use
            # it to compute the minimum enclosing circle and
            # centroid
            c = max(contours, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

            # only proceed if the radius meets a minimum size
            if radius > 10:
                # draw the circle and centroid on the img_frame,
                # then update the list of tracked points
                cv2.circle(img_frame, (int(x), int(y)), int(radius),
                    (255, 255, 255), 2)
                cv2.circle(img_frame, center, 5, (255, 255, 255), -1)


        cv2.imshow("other", res)
        cv2.imshow("Frame", img_frame)

        key = cv2.waitKey(1) & 0xFF

        # if the 'q' key is pressed, stop the loop
        if key == ord("q"):
            break
    # cleanup the camera and close any open windows
    camera.release()
    cv2.destroyAllWindows()
    vs.stop()
main()


