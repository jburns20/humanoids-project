import cv2
import numpy as np
from matplotlib import pyplot as plt
from threading import Thread
import imutils  # not neccesary but remove line 174
from math import pi
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



def main():
    # ####upper and lower bounds for colors
    # yellow bounds from:
    # https://stackoverflow.com/questions/9179189/detect-yellow-color-in-opencv

    vs = WebcamVideoStream(src=0).start()
    while True:

        blur = cv2.GaussianBlur(gray,(9,9),0)
        ret,thresh = cv2.threshold(blur,127,255,0)
        # kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (10, 10))
        # closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)

        im2, contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        im3, contoursTT, hierarchyTT = cv2.findContours(edges,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        if len(contours) >0:
            c = max(contours, key=cv2.contourArea)
        # cv2.imshow("eggg", im2)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
        # cv2.drawContours(img, contours, -1, (255,255,0), 3)
        cv2.drawContours(img, contoursTT, -1, (0,0,255), 3)
        gray2 = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        imgsub = cv2.subtract(cp,gray2)
        # lines = cv2.HoughLinesP(edges,1,np.pi/180,80,30,10)
        # for x1,y1,x2,y2 in lines[0]:
        #     cv2.line(img,(x1,y1),(x2,y2),(0,255,0),2)

        # # cv2.imshow("affs", imgsub) 
        # (image, method, dp, minDist[, circles[, param1[, param2[, minRadius[, maxRadius]]]]])
        lines = cv2.HoughLinesP(edges, 1, pi/2, 2, None, 30, 1)
        if lines is not None:
            for line in lines[0]:
                    pt1 = (line[0],line[1])
                    pt2 = (line[2],line[3])
                    cv2.line(edges, pt1, pt2, (0,0,255), 3)
        # circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1.2, 100)
        # mask = cv2.erode(imgsub, None, iterations=3)
        # mask = cv2.dilate(mask, None, iterations=3)   
        cv2.imshow("other", edges) 

  
                    # edges = cv2.Canny(img,100,200)
        # gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


        # detector = cv2.SimpleBlobDetector_create()
 
        # # Detect blobs.
        # keypoints = detector.detect(img)
 
        # # Draw detected blobs as red circles.
        # # cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS ensures the size of the circle corresponds to the size of blob
        # im_with_keypoints = cv2.drawKeypoints(gray, keypoints, np.array([]), (0,0,255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        # gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        # linek = np.zeros((11,11),dtype=np.uint8)
        # linek[5,...]=1
        # x=cv2.morphologyEx(gray, cv2.MORPH_OPEN, linek ,iterations=1)
        # gray-=x
        # cv2.imshow('gray',edges)
        # lines = cv2.HoughLines(edges,1,np.pi/180,200)
        # for rho,theta in lines[0]:
        #     a = np.cos(theta)
        #     b = np.sin(theta)
        #     x0 = a*rho
        #     y0 = b*rho
        #     x1 = int(x0 + 1000*(-b))
        #     y1 = int(y0 + 1000*(a))
        #     x2 = int(x0 - 1000*(-b))
        #     y2 = int(y0 - 1000*(a))

        #     cv2.line(img,(x1,y1),(x2,y2),(0,0,255),2)
        # cv2.imshow("other", img)
        key = cv2.waitKey(1) & 0xFF

        # if the 'q' key is pressed, stop the loop
        if key == ord("q"):
            break
    # cleanup the camera and close any open windows
    cv2.destroyAllWindows()
    vs.stop()
main()


