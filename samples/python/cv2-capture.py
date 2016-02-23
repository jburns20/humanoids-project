 
import cv2

stream1 = cv2.VideoCapture(0)   #0 is the id of video device.0 if you have only one camera.

if (not stream1.isOpened()):     #check if video device has been initialised
    print "cannot open camera"

#unconditional loop
success = True
while (success):
    (success, frame) = stream1.read()
    cv2.imshow("cam", frame)

