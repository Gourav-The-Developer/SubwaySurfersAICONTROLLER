#Import necessary modules
import cv2
import imutils
import numpy as np
# import GameSelenium as GSEL

from collections import deque
import time
import pyautogui
from threading import Thread

#Class implemeting seperate threading for reading of frames.
class WebcamVideoStream:
    def __init__(self):
        # self.stream = cv2.VideoCapture('http://192.168.1.4:8080/video')
        self.stream = cv2.VideoCapture(0)

        self.ret, self.frame = self.stream.read()
        self.stopped = False
    def start(self):
        Thread(target = self.update, args=()).start()
        return self
    def update(self):
        while True:
            if self.stopped:
                return
            self.ret, self.frame = self.stream.read()
    def read(self):
        return self.frame
    def stop(self):
        self.stopped = True

"""class VideoShow:
    def __init__(self, frame = None):
        self.frame = frame
        self.stopped = False
    def start(self):
        while not self.stopped:
            cv2.imshow('Game Control Window', self.frame)
            if(cv2.waitKey(1) == ord('q')):
                self.stopped = True
    def stop(self):
        self.stopped = True
"""
#Define HSV colour range for green, red, blue colour objects
greenLower=(30,30,0)
greenUpper=(85,255,255)

redLower=(150,50,0)
redUpper=(179,255,255)

blueLower=(95,90,0)
blueUpper=(150,255,255)

#Used in deque structure to store no. of given buffer points
buffer = 20

#Used so that pyautogui doesn't click the center of the screen at every frame
flag = 0

#Points deque structure storing 'buffer' no. of object coordinates
blue_pts = deque(maxlen = buffer)
green_pts = deque(maxlen = buffer)
red_pts = deque(maxlen = buffer)
#Counts the minimum no. of frames to be detected where direction change occurs
counter = 0
#Change in direction is stored in dX, dY
(dX, dY) = (0, 0)
#Variable to store direction string
direction = ''
#Last pressed variable to detect which key was pressed by pyautogui
last_pressed = ''

#Sleep for 2 seconds to let camera initialize properly.
time.sleep(2)

#Use pyautogui function to detect width and height of the screen
width,height = pyautogui.size()

#Start video capture in a seperate thread from main thread.
vs = WebcamVideoStream().start()
#video_shower = VideoShow(vs.read()).start()

#Click on the centre of the screen, game window should be placed here.
pyautogui.click(int(width/2), int(height/2))

while True:

    '''game_window = pyautogui.locateOnScreen(r'images\SnakeGameWelcomeScreen.png')
    game_window_center = pyautogui.center(game_window)
    pyautogui.click(game_window_center)'''

    #Store the readed frame in frame
    frame = vs.read()
    #Flip the frame to avoid mirroring effect
    frame = cv2.flip(frame,1)
    #Resize the given frame to a 600*600 window
    frame = imutils.resize(frame, width = 600)
    #Blur the frame using Gaussian Filter of kernel size 11, to remove excessivve noise
    blurred_frame = cv2.GaussianBlur(frame, (5,5), 0)
    cv2.imshow("Blurred Window", blurred_frame)
    cv2.waitKey(1)
    #Convert the frame to HSV, as HSV allow better segmentation.
    hsv_converted_frame = cv2.cvtColor(blurred_frame, cv2.COLOR_BGR2HSV)

      #Create a mask for the frame, showing green values
    # mask = cv2.inRange(hsv_converted_frame, greenLower, greenUpper)
    # cv2.imshow("mask Window", mask)
    # cv2.waitKey(1)
    # #Erode the masked output to delete small white dots present in the masked image
    # mask = cv2.erode(mask, None, iterations = 2)
    # cv2.imshow("eroded Window", mask)
    # cv2.waitKey(1)
    # #Dilate the resultant image to restore our target
    # mask = cv2.dilate(mask, None, iterations = 2)
    # cv2.imshow("dilated Window", mask)
    # cv2.waitKey(1)
    blue_mask = cv2.dilate(cv2.erode(cv2.inRange(hsv_converted_frame, blueLower, blueUpper), None, iterations = 2), None, iterations = 2)
    
    #Find all contours in the masked image
    cnts, hierarchy = cv2.findContours(blue_mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    #Define center of the ball to be detected as None
    center = None

    #If any object is detected, then only proceed
    if(len(cnts) > 0):
        #Find the contour with maximum area
        c = max(cnts, key = cv2.contourArea)
        cv2.drawContours(frame, c, -1, (0,255,0), 3)
        x, y, w, h = cv2.boundingRect(c)
        frame = cv2.rectangle(frame, (x, y), 
                                       (x + w, y + h),
                                       (0, 255, 0), 2)
        #Find the center of the circle, and its radius of the largest detected contour.
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        #Calculate the centroid of the ball, as we need to draw a circle around it.
        M = cv2.moments(c)
        center = (int(M['m10'] / M['m00']), int(M['m01'] / M['m00']))

        #Proceed only if a ball of considerable size is detected
        if radius > 20:
            #Draw circles around the object as well as its centre
            cv2.putText(frame, "Blue Colour", (int(x), int(y)),
                        cv2.FONT_HERSHEY_SIMPLEX, 
                        1.0, (0, 255, 0))
            cv2.circle(frame, (int(x), int(y)), int(radius), (0,255,255), 2)
            cv2.circle(frame, center, 5, (0,255,255), -1)
            #Append the detected object in the frame to pts deque structure
            blue_pts.appendleft(center)


    green_mask = cv2.dilate(cv2.erode(cv2.inRange(hsv_converted_frame, greenLower, greenUpper), None, iterations = 2), None, iterations = 2)
    #Find all contours in the masked image
    cnts, hierarchy = cv2.findContours(green_mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    #Define center of the ball to be detected as None
    center = None

    #If any object is detected, then only proceed
    if(len(cnts) > 0):
        #Find the contour with maximum area
        c = max(cnts, key = cv2.contourArea)
        cv2.drawContours(frame, c, -1, (0,255,0), 3)
        x, y, w, h = cv2.boundingRect(c)
        frame = cv2.rectangle(frame, (x, y), 
                                       (x + w, y + h),
                                       (0, 255, 0), 2)
        #Find the center of the circle, and its radius of the largest detected contour.
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        #Calculate the centroid of the ball, as we need to draw a circle around it.
        M = cv2.moments(c)
        center = (int(M['m10'] / M['m00']), int(M['m01'] / M['m00']))

        #Proceed only if a ball of considerable size is detected
        if radius > 20:
            #Draw circles around the object as well as its centre
            cv2.putText(frame, "Green Colour", (int(x), int(y)),
                        cv2.FONT_HERSHEY_SIMPLEX, 
                        1.0, (0, 255, 0))
            cv2.circle(frame, (int(x), int(y)), int(radius), (0,255,255), 2)
            cv2.circle(frame, center, 5, (0,255,255), -1)
            #Append the detected object in the frame to pts deque structure
            green_pts.appendleft(center)


    red_mask = cv2.dilate(cv2.erode(cv2.inRange(hsv_converted_frame, redLower, redUpper), None, iterations = 2), None, iterations = 2)
    #Find all contours in the masked image
    cnts, hierarchy = cv2.findContours(red_mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    #Define center of the ball to be detected as None
    center = None

    #If any object is detected, then only proceed
    if(len(cnts) > 0):
        #Find the contour with maximum area
        c = max(cnts, key = cv2.contourArea)
        cv2.drawContours(frame, c, -1, (0,255,0), 3)
        x, y, w, h = cv2.boundingRect(c)
        frame = cv2.rectangle(frame, (x, y), 
                                       (x + w, y + h),
                                       (0, 255, 0), 2)
        #Find the center of the circle, and its radius of the largest detected contour.
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        #Calculate the centroid of the ball, as we need to draw a circle around it.
        M = cv2.moments(c)
        center = (int(M['m10'] / M['m00']), int(M['m01'] / M['m00']))

        #Proceed only if a ball of considerable size is detected
        if radius > 20:
            #Draw circles around the object as well as its centre
            cv2.putText(frame, "Red Colour", (int(x), int(y)),
                        cv2.FONT_HERSHEY_SIMPLEX, 
                        1.0, (0, 255, 0))
            cv2.circle(frame, (int(x), int(y)), int(radius), (0,255,255), 2)
            cv2.circle(frame, center, 5, (0,255,255), -1)
            #Append the detected object in the frame to pts deque structure
            red_pts.appendleft(center)
    cv2.imshow("Final Image", frame)
    cv2.waitKey(1)

    