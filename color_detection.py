# Import necessary modules
import cv2
import imutils
import numpy as np
# import GameSelenium as GSEL

from collections import deque
import time
import pyautogui
from threading import Thread

# Class implemeting seperate threading for reading of frames.
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
    def _init_(self, frame = None):
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
# Define HSV colour range for green, red, blue colour objects
greenLower = (30, 30, 0)
greenUpper = (85, 255, 255)

redLower = (150, 50, 0)
redUpper = (179, 255, 255)
blueLower = (95, 90, 0)
blueUpper = (150, 255, 255)

# Used in deque structure to store no. of given buffer points
buffer = 20

# Used so that pyautogui doesn't click the center of the screen at every frame
flag = 0

# Points deque structure storing 'buffer' no. of object coordinates
blue_pts = deque(maxlen=buffer)
green_pts = deque(maxlen=buffer)
red_pts = deque(maxlen=buffer)
# Counts the minimum no. of frames to be detected where direction change occurs
counter = 0
NeutralPos=True
Green_NeutralPos=True
Red_NeutralPos=True
Blue_NeutralPos=True
# Change in direction is stored in dX, dY
(dX, dY) = (0, 0)
# Variable to store direction string
red_direction = ''
green_direction = ''
blue_direction = ''
# Last pressed variable to detect which key was pressed by pyautogui
last_pressed = ''

# Sleep for 2 seconds to let camera initialize properly.
time.sleep(2)

# Use pyautogui function to detect width and height of the screen
width, height = pyautogui.size()

# Start video capture in a seperate thread from main thread.
vs = WebcamVideoStream().start()
# video_shower = VideoShow(vs.read()).start()

# Click on the centre of the screen, game window should be placed here.
pyautogui.click(int(width / 2), int(height / 2))

while True:

    '''game_window = pyautogui.locateOnScreen(r'images\SnakeGameWelcomeScreen.png')
    game_window_center = pyautogui.center(game_window)
    pyautogui.click(game_window_center)'''

    # Store the readed frame in frame
    frame = vs.read()
    # Flip the frame to avoid mirroring effect
    frame = cv2.flip(frame, 1)
    # Resize the given frame to a 600*600 window
    frame = imutils.resize(frame, width=600)
    # Blur the frame using Gaussian Filter of kernel size 11, to remove excessivve noise
    blurred_frame = cv2.GaussianBlur(frame, (5, 5), 0)
    cv2.imshow("Blurred Window", blurred_frame)
    cv2.waitKey(1)
    # Convert the frame to HSV, as HSV allow better segmentation.
    hsv_converted_frame = cv2.cvtColor(blurred_frame, cv2.COLOR_BGR2HSV)

    # Create a mask for the frame, showing green values
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
    blue_mask = cv2.dilate(cv2.erode(cv2.inRange(hsv_converted_frame, blueLower, blueUpper), None, iterations=2), None,
                           iterations=2)

    # Find all contours in the masked image
    blue_cnts, hierarchy = cv2.findContours(blue_mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Define center of the ball to be detected as None
    center = None

    # If any object is detected, then only proceed
    if (len(blue_cnts) > 0):
        # Find the contour with maximum area
        blue_c = max(blue_cnts, key=cv2.contourArea)
        cv2.drawContours(frame, blue_c, -1, (0, 255, 0), 3)
        blue_x, blue_y, blue_w, blue_h = cv2.boundingRect(blue_c)
        frame = cv2.rectangle(frame, (blue_x, blue_y),
                              (blue_x + blue_w, blue_y + blue_h),
                              (0, 255, 0), 2)
        # Find the center of the circle, and its radius of the largest detected contour.
        ((blue_x, blue_y), radius) = cv2.minEnclosingCircle(blue_c)
        # Calculate the centroid of the ball, as we need to draw a circle around it.
        M = cv2.moments(blue_c)
        center = (int(M['m10'] / M['m00']), int(M['m01'] / M['m00']))

        # Proceed only if a ball of considerable size is detected
        if radius > 20:
            # Draw circles around the object as well as its centre
            cv2.putText(frame, "Blue Colour", (int(blue_x), int(blue_y)),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1.0, (0, 255, 0))
            cv2.circle(frame, (int(blue_x), int(blue_y)), int(radius), (0, 255, 255), 2)
            cv2.circle(frame, center, 5, (0, 255, 255), -1)
            # Append the detected object in the frame to pts deque structure
            blue_pts.appendleft(center)


    green_mask = cv2.dilate(cv2.erode(cv2.inRange(hsv_converted_frame, greenLower, greenUpper), None, iterations=2),
                            None, iterations=2)
    # Find all contours in the masked image
    green_cnts, hierarchy = cv2.findContours(green_mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Define center of the ball to be detected as None
    center = None

    # If any object is detected, then only proceed
    if (len(green_cnts) > 0):
        # Find the contour with maximum area
        green_c = max(green_cnts, key=cv2.contourArea)
        cv2.drawContours(frame, green_c, -1, (0, 255, 0), 3)
        green_x, green_y, green_w, green_h = cv2.boundingRect(green_c)
        frame = cv2.rectangle(frame, (green_x, green_y),
                              (green_x + green_w, green_y + green_h),
                              (0, 255, 0), 2)
        # Find the center of the circle, and its radius of the largest detected contour.
        ((green_x, green_y), radius) = cv2.minEnclosingCircle(green_c)
        # Calculate the centroid of the ball, as we need to draw a circle around it.
        M = cv2.moments(green_c)
        center = (int(M['m10'] / M['m00']), int(M['m01'] / M['m00']))

        # Proceed only if a ball of considerable size is detected
        if radius > 20:
            # Draw circles around the object as well as its centre
            cv2.putText(frame, "Green Colour", (int(green_x), int(green_y)),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1.0, (0, 255, 0))
            cv2.circle(frame, (int(green_x), int(green_y)), int(radius), (0, 255, 255), 2)
            cv2.circle(frame, center, 5, (0, 255, 255), -1)
            # Append the detected object in the frame to pts deque structure
            green_pts.appendleft(center)

    red_mask = cv2.dilate(cv2.erode(cv2.inRange(hsv_converted_frame, redLower, redUpper), None, iterations=2), None,
                          iterations=2)
    # Find all contours in the masked image
    red_cnts, hierarchy = cv2.findContours(red_mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Define center of the ball to be detected as None
    center = None

    # If any object is detected, then only proceed
    if (len(red_cnts) > 0):
        # Find the contour with maximum area
        red_c = max(red_cnts, key=cv2.contourArea)
        cv2.drawContours(frame, red_c, -1, (0, 255, 0), 3)
        red_x, red_y, red_w, red_h = cv2.boundingRect(red_c)
        frame = cv2.rectangle(frame, (red_x, red_y,),
                              (red_x + red_w, red_y + red_h),
                              (0, 255, 0), 2)
        # Find the center of the circle, and its radius of the largest detected contour.
        ((red_x, red_y), radius) = cv2.minEnclosingCircle(red_c)
        # Calculate the centroid of the ball, as we need to draw a circle around it.
        M = cv2.moments(red_c)
        center = (int(M['m10'] / M['m00']), int(M['m01'] / M['m00']))

        # Proceed only if a ball of considerable size is detected
        if radius > 20:
            # Draw circles around the object as well as its centre
            cv2.putText(frame, "Red Colour", (int(red_x), int(red_y)),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1.0, (0, 255, 0))
            cv2.circle(frame, (int(red_x), int(red_y)), int(radius), (0, 255, 255), 2)
            cv2.circle(frame, center, 5, (0, 255, 255), -1)
            # Append the detected object in the frame to pts deque structure
            red_pts.appendleft(center)
    cv2.imshow("Final Image", frame)
    cv2.waitKey(1)
    # Using numpy arange function for better performance. Loop till all detected points
    for blue_i in np.arange(1, len(blue_pts)):
        # If no points are detected, move on.
        if (blue_pts[blue_i - 1] == None or blue_pts[blue_i] == None):
            print(blue_pts)
            continue

        # If atleast 10 frames have direction change, proceed
        if counter >= 10 and blue_i == 1:
            try:
                if blue_pts[-10] is not None:
                    # Calculate the distance between the current frame and 10th frame before
                    dX = blue_pts[-10][0] - blue_pts[blue_i][0]
                    dY = blue_pts[-10][1] - blue_pts[blue_i][1]
                    (dirX, dirY) = ('', '')

                    # If distance is greater than 50 pixels, considerable direction change has occured.
                    if 400>np.abs(dY)>200 :
                        Blue_NeutralPos = True
                    if np.abs(dX) > 50:
                        dirX = 'West' if np.sign(dX) == 1 else 'East'

                    if np.abs(dY) > 50:
                        dirY = 'North' if np.sign(dY) == 1 else 'South'

                    # Set direction variable to the detected direction
                    blue_direction = dirX if dirX != '' else dirY
                    # Write the detected direction on the frame
                    cv2.putText(frame, blue_direction, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
            except:
                blue_direction = "error"

        # Draw a trailing red line to depict motion of the object.
        thickness = int(np.sqrt(buffer / float(blue_i + 1)) * 2.5)
        cv2.line(frame, blue_pts[blue_i - 1], blue_pts[blue_i], (0, 0, 255), thickness)
    for red_i in np.arange(1, len(red_pts)):
        # If no points are detected, move on.
        if (red_pts[red_i - 1] == None or red_pts[red_i] == None):
            print(red_pts)
            continue

        # If atleast 10 frames have direction change, proceed
        if counter >= 10 and red_i == 1:
            try:
                if red_pts[-10] is not None:
                    # Calculate the distance between the current frame and 10th frame before
                    dX = red_pts[-10][0] - red_pts[red_i][0]
                    dY = red_pts[-10][1] - red_pts[red_i][1]
                    (dirX, dirY) = ('', '')

                    # If distance is greater than 50 pixels, considerable direction change has occured.
                    if 400>np.abs(dY)>200 :
                        Red_NeutralPos = True
                    if np.abs(dX) > 50:
                        dirX = 'West' if np.sign(dX) == 1 else 'East'

                    if np.abs(dY) > 50:
                        dirY = 'North' if np.sign(dY) == 1 else 'South'

                    # Set direction variable to the detected direction
                    red_direction = dirX if dirX != '' else dirY
                    # Write the detected direction on the frame
                    cv2.putText(frame, red_direction, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
            except:
                red_direction = "error"

        # Draw a trailing red line to depict motion of the object.
        thickness = int(np.sqrt(buffer / float(red_i + 1)) * 2.5)
        cv2.line(frame, red_pts[red_i - 1], red_pts[red_i], (0, 0, 255), thickness)
    for green_i in np.arange(1, len(green_pts)):
        # If no points are detected, move on.
        if (green_pts[green_i - 1] == None or green_pts[green_i] == None):
            print(green_pts)
            continue

        # If atleast 10 frames have direction change, proceed
        if counter >= 10 and green_i == 1:
            try:
                if green_pts[-10] is not None:
                    # Calculate the distance between the current frame and 10th frame before
                    dX = green_pts[-10][0] - green_pts[green_i][0]
                    dY = green_pts[-10][1] - green_pts[green_i][1]
                    (dirX, dirY) = ('', '')

                    # If distance is greater than 50 pixels, considerable direction change has occured.
                    
                    if 400>np.abs(dY)>200 :
                        Green_NeutralPos = True
                    if np.abs(dX) > 50:
                        dirX = 'West' if np.sign(dX) == 1 else 'East'

                    if np.abs(dY) > 50:
                        dirY = 'North' if np.sign(dY) == 1 else 'South'

                    # Set direction variable to the detected direction
                    green_direction = dirX if dirX != '' else dirY
                    # Write the detected direction on the frame
                    cv2.putText(frame, green_direction, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
            except:
                green_direction = "error"

        # Draw a trailing red line to depict motion of the object.
        thickness = int(np.sqrt(buffer / float(green_i + 1)) * 2.5)
        cv2.line(frame, green_pts[green_i - 1], green_pts[green_i], (0, 0, 255), thickness)

    if red_direction == blue_direction == green_direction:
        direction=red_direction
        
        if Blue_NeutralPos==Red_NeutralPos==Green_NeutralPos:
            NeutralPos=Blue_NeutralPos
        
        if direction != '':
            red_Coords = red_pts[0]
            blue_Coords = blue_pts[0]
            green_Coords = green_pts[0]
            print("BeforeRed_Pts", red_pts)
            print("I", red_i)
            for x in range(0, 19):
                
                red_pts.appendleft(red_Coords)
                blue_pts.appendleft(blue_Coords)
                green_pts.appendleft(green_Coords)
            print("redPts:",red_pts)
        #If deteced direction is East, press right button
            if direction == 'East':
                direction=''
                # pyautogui.press('right')
                pyautogui.click(int(width/2), int(height/2))
                # GSEL.clickRight()
                last_pressed = 'right'
                print("Right Pressed")
                #pyautogui.PAUSE = 2
            #If deteced direction is West, press Left button
            elif direction == 'West':
                
                # pyautogui.press('left')
                pyautogui.click(int(width/2), int(height/2))
                # GSEL.clickLEFT()
                direction=''
                last_pressed = 'left'
                print("Left Pressed")
                #pyautogui.PAUSE = 2
            #if detected direction is North, press Up key
            elif direction == 'North' and NeutralPos:
                last_pressed = 'up'
                direction=''
                NeutralPos=False
                pyautogui.click(int(width/2), int(height/2))
                # GSEL.clickUP()
                # pyautogui.press('up')
                print("Up Pressed")
                #pyautogui.PAUSE = 2
            #If detected direction is South, press down key
            elif direction == 'South' and NeutralPos:
                NeutralPos=False
                direction=''
                # pyautogui.press('down')
                # GSEL.clickDOWN()
                pyautogui.click(int(width/2), int(height/2))
                last_pressed = 'down'
                print("Down Pressed")
                #pyautogui.PAUSE = 2


    #video_shower.frame = frame
    #Show the output frame.
    cv2.imshow('Game Control Window', frame)
    key = cv2.waitKey(1) & 0xFF
    #Update counter as the direction change has been detected.
    counter += 1

    #If pyautogui has not clicked on center, click it once to focus on game window.
    if (flag == 0):
        pyautogui.click(int(width/2), int(height/2))
        flag = 1

    #If q is pressed, close the window
    if(key == ord('q')):
        break
#After all the processing, release webcam and destroy all windows
vs.stop()
cv2.destroyAllWindows()
# GSEL.closeWebDriver()