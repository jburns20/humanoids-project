#!/usr/bin/env python

import numpy as np
import cv2
import imutils

help_message = '''
USAGE: opt_flow.py [<video_source>]

Keys:
 1 - toggle HSV flow visualization
 2 - toggle glitch

'''


def lenlen(x1,y1,x2,y2):
	return ((((x1-x2)**2) +((y1-y2)**2))**.5)

def draw_flow(img, flow, step=16):
    h, w = img.shape[:2]
    y, x = np.mgrid[step/2:h:step, step/2:w:step].reshape(2,-1)
    fx, fy = flow[y,x].T
    lines = np.vstack([x, y, x+fx, y+fy]).T.reshape(-1, 2, 2)
    lines = np.int32(lines + 0.5)
    line2 = []
    vis = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

    for line in lines:
        x1 = line[0][0]
        x2 = line[1][0]
        y1 = line[0][1]
        y2 = line[1][1]
        if (lenlen(x1,y1,x2,y2) > 10):
            line2.append(line)

        # cv2.circle(vis, (x1, y1), 1, (0, 255, 0), -1)


    # cv2.polylines(vis, line2, 0, (0, 255, 0))
    # for (x1, y1), (x2, y2) in lines:
    #     cv2.circle(vis, (x1, y1), 1, (0, 255, 0), -1)
    return (vis, line2)

def draw_hsv(flow):
    h, w = flow.shape[:2]
    fx, fy = flow[:,:,0], flow[:,:,1]
    ang = np.arctan2(fy, fx) + np.pi
    v = np.sqrt(fx*fx+fy*fy)
    hsv = np.zeros((h, w, 3), np.uint8)
    hsv[...,0] = ang*(180/np.pi/2)
    hsv[...,1] = 255
    hsv[...,2] = np.minimum(v*4, 255)
    bgr = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    return bgr

def warp_flow(img, flow):
    h, w = flow.shape[:2]
    flow = -flow
    flow[:,:,0] += np.arange(w)
    flow[:,:,1] += np.arange(h)[:,np.newaxis]
    res = cv2.remap(img, flow, None, cv2.INTER_LINEAR)
    return res

def createMask(img, lowerbound, upperbound):
    # convert image into HSV.
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    # construct a mask to isolate the yellow glove from the screen
    mask = cv2.inRange(hsv, lowerbound, upperbound)
    mask = cv2.erode(mask, None, iterations=3)
    mask = cv2.dilate(mask, None, iterations=3)
    return mask






if __name__ == '__main__':
    import sys
    print help_message
    try:
        fn = sys.argv[1]
    except:
        fn = 0
    lower_blue = np.array([70, 92, 88])
    upper_blue = np.array([141, 255, 255])

    # cam = cv2.VideoCapture(0)
    cam = cv2.VideoCapture("slowmo.mp4")
    ret, prev = cam.read()
    prev = imutils.resize(prev, width=700)

    prevgray = cv2.cvtColor(prev, cv2.COLOR_BGR2GRAY)
    show_hsv = False
    show_glitch = False
    cur_glitch = prev.copy()
    bottomRight = 0;
    topLeft = 0;

    while True:
        ret, img = cam.read()
        img = imutils.resize(img, width=700)

        mask = createMask(img, lower_blue, upper_blue)
        cv2.imshow("asdf",mask)
        contours = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                                    cv2.CHAIN_APPROX_SIMPLE)[-2]
        cnts = sorted(contours, key = cv2.contourArea, reverse = True)[:2]

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
            cv2.circle(img, bottomRight, 1, [0, 0, 255], 2)
            cv2.circle(img, topleft, 1, [0, 0, 255], 2)
        else:
            bottomRight = 0
            topLeft = 0
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        flow = cv2.calcOpticalFlowFarneback(prevgray, gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)
        prevgray = gray
        (flowDraw,lines) = draw_flow(gray, flow)
        # cv2.imshow('flow', flowDraw)
        if (bottomRight and topleft):
            cv2.rectangle(flowDraw, topleft, bottomRight, [255,0,0], thickness=1, lineType=8, shift=0)
        count = 0
        line3 =[]
        if (bottomRight and topleft):
            for line in lines :
                x1 = line[0][0]
                x2 = line[1][0]
                y1 = line[0][1]
                y2 = line[1][1]
                if ((topleft[0]< line[0][0] < bottomRight[0]) and (topleft[1]< line[0][1] < bottomRight[1]) and ((y1-y2)/(x1-x2) < 0)):
                    count += 1
                    line3.append(line)
                    #cv2.polylines(vis, line2, 0, (0, 255, 0))

    	if ((bottomRight and topleft) and (count>0)):		
            print("FlOW DETECTED:")
        else:
            print("no flow")
        if ((bottomRight and topleft) and (count > 10)):      
            print("fast")
        elif (count > 5 ):
            print("slow")
        if (bottomRight and topleft):
            cv2.polylines(flowDraw, line3, 0, (0, 255, 0))
        
        cv2.imshow('flow', flowDraw)



        ch = 0xFF & cv2.waitKey(5)
        if ch == 27:
            break
    cv2.destroyAllWindows()
