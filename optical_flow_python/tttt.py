import matplotlib.pyplot as plt
from skimage import data, color, img_as_float, img_as_ubyte
from skimage.feature import canny
from skimage.transform import hough_ellipse
from skimage.draw import ellipse_perimeter
import cv2
import numpy as np
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
    # Load picture, convert to grayscale and detect edges
    camera = cv2.VideoCapture(0)
    (ret, img) = camera.read()
    cv2.imshow("blah",img)
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    cp = gray.copy()
    edges = cv2.Canny(gray,50,150,apertureSize = 3)
    print "hi"
    edges = img_as_float(edges)
    print "hi"

    # Perform a Hough Transform
    # The accuracy corresponds to the bin size of a major axis.
    # The value is chosen in order to get a single high accumulator.
    # The threshold eliminates low accumulators
    result = hough_ellipse(edges, accuracy=20, threshold=250, min_size=100, max_size=120)
    print "hi"
    result.sort(order='accumulator')
    print result

    # Estimated parameters for the ellipse
    if (len(result) > 0):
        print "apple"
        best = list(result[-1])
        yc, xc, a, b = [int(round(x)) for x in best[1:5]]
        orientation = best[5]

        # Draw the ellipse on the original image
        cy, cx = ellipse_perimeter(yc, xc, a, b, orientation)
        image_rgb[cy, cx] = (0, 0, 255)
        # Draw the edge (white) and the resulting ellipse (red)
        edges = color.gray2rgb(edges)
        edges[cy, cx] = (25, 0, 255)

    # fig2, (ax1, ax2) = plt.subplots(ncols=2, nrows=1, figsize=(8, 4), sharex=True,
    #                                 sharey=True,
    #                                 subplot_kw={'adjustable':'box-forced'})

    # ax1.set_title('Original picture')
    cv2.imshow("apple",img_as_ubyte(edges))


main()