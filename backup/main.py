from collections import deque
import numpy as np
import argparse
import imutils
import cv2
from PIL import Image
import pyautogui
#import subprocess
import ctypes
from ctypes import *
import win32api
import win32con
import win32com
import win32com.client
import win32gui
import win32ui
import time

from pynput.keyboard import Key, Controller
keyboard = Controller()



screenWidth, screenHeight = pyautogui.size()

def RGB2HSV(R, G, B):
        color = np.uint8([[[B, G, R]]])
        hsvc = cv2.cvtColor(color,cv2.COLOR_BGR2HSV)
        hsv = (hsvc[0][0][0], hsvc[0][0][1], hsvc[0][0][2])
        print(hsv)
        return (hsv[0], hsv[1], hsv[2])


def createRectAHK(x, y, width, height, center):
        if center:
                x = x - (width/2)
                y = y - (height/2)
        width = width/2
        height = height/2

        program = 'createRect.exe'
        arg1 = str(x)
        arg2 = str(y)
        arg3 = str(width)
        arg4 = str(height)
        subprocess.call([program, arg1, arg2, arg3, arg4])

def moveMouseRel(xOffset, yOffset):
        ctypes.windll.user32.mouse_event(0x0001, xOffset, yOffset, 0, 0)



# construct the argument parse and parse the arguments

ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",
        help="path to the (optional) video file")
ap.add_argument("-b", "--buffer", type=int, default=32,
        help="max buffer size")
args = vars(ap.parse_args())


# define the lower and upper boundaries of the color
# in the HSV color space
#lw = RGB2HSV(148, 159, 0)
#up = RGB2HSV(244, 249, 170)
#colorLower = ( int(lw[0]) , int(lw[1]), int(lw[2]) )
#colorUpper = ( int(up[0]) , int(up[1]), int(up[2]) )
#colorMiddle = RGB2HSV(223, 239, 0)


# In HSV:
#H: 0 - 180, S: 0 - 255, V: 0 - 255

# colorLower = np.array([50,80,20])#green
# colorUpper = np.array([70,255,255])

colorLower1 = np.array([50,80,20])#green
colorUpper1 = np.array([70,255,255])

colorLower2 = np.array([100,80,20])#red
colorUpper2 = np.array([130,255,255])

colorLower3 = np.array([80,80,20])#yellow
colorUpper3 = np.array([90,255,255])

colorLower4 = np.array([10,80,20])#blue
colorUpper4 = np.array([30,255,255])

colorLower5 = np.array([95,80,20])#orange
colorUpper5 = np.array([110,255,255])



# initialize the list of tracked points, the frame counter,
# and the coordinate deltas
pts = deque(maxlen=args["buffer"])
counter = 0
(dX, dY) = (0, 0)
direction = ""


bufferX = 400
bufferY = 280
centerX = screenWidth/2
centerY = screenHeight/2

x1 = centerX - bufferX
y1 = centerY - bufferY

x2 = centerX + bufferX
y2 = centerY + bufferY

w = bufferX*2
h = bufferY*2



# #get window position and info
# hwnd = win32gui.FindWindow(None, "Clone Hero")
# #hwnd = win32gui.GetDesktopWindow()#for screenshot of entire screen
# l, t, r, b = win32gui.GetWindowRect(hwnd)
# windowHeight = b-t
# windowWidth = r-l
# windowCenterX = windowWidth/2
# windowCenterY = windowHeight/2


# # SSx1 = int(windowCenterX - bufferX)
# # SSy1 = int(windowCenterY - bufferY)
# SSx1 = l
# SSy1 = t
# SSWidth = 1280
# SSHeight = 680




toggle = False
timeSinceLastToggle = time.clock()

toggle2 = False
timeSinceLastKey = time.clock()

# loop
while (1):
        
        start = time.clock()


        #get window position and info
        hwnd = win32gui.FindWindow(None, "Clone Hero")
        l, t, r, b = win32gui.GetWindowRect(hwnd)
        SSx1 = l+390
        SSy1 = t
        SSWidth = 500
        SSHeight = 640
        
        #get window position and info
        hwnd = win32gui.FindWindow(None, "Clone Heroa")
        #hwnd = win32gui.GetDesktopWindow()#for screenshot of entire screen
        
        wDC = win32gui.GetWindowDC(hwnd)
        myDC = win32ui.CreateDCFromHandle(wDC)
        newDC = myDC.CreateCompatibleDC()
        myBitMap = win32ui.CreateBitmap()
        myBitMap.CreateCompatibleBitmap(myDC, SSWidth, SSHeight)
        newDC.SelectObject(myBitMap)
        newDC.BitBlt((0,0),(SSWidth, SSHeight) , myDC, (SSx1,SSy1), win32con.SRCCOPY)

        bmpinfo = myBitMap.GetInfo()
        bmpstr = myBitMap.GetBitmapBits(True)
        img = Image.frombuffer(
            'RGB',
            (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
            bmpstr, 'raw', 'BGRX', 0, 1)

        # Free Resources
        myDC.DeleteDC()
        newDC.DeleteDC()
        win32gui.ReleaseDC(hwnd, wDC)
        win32gui.DeleteObject(myBitMap.GetHandle())
        
        #img = ImageGrab.grab(bbox=(x1, y1, x2, y2))#.crop(box) #x, y, w, h
        img_np = np.array(img)
        frame = cv2.cvtColor(img_np, cv2.COLOR_BGR2RGB)
        #frame = imutils.resize(frame, width=600)
        hsv = cv2.cvtColor(img_np, cv2.COLOR_BGR2HSV)

        #contours = [1, 2, 3, 4, 5]

        mask = cv2.inRange(hsv, colorLower1, colorUpper1)

        pts = []

        for i in range(0, 5):

            if(i == 0):
                mask = cv2.inRange(hsv, colorLower1, colorUpper1)
            elif(i == 1):
                mask = cv2.inRange(hsv, colorLower2, colorUpper2)
            elif(i == 2):
                mask = cv2.inRange(hsv, colorLower3, colorUpper3)
            elif(i == 3):
                mask = cv2.inRange(hsv, colorLower4, colorUpper4)
            elif(i == 4):
                mask = cv2.inRange(hsv, colorLower5, colorUpper5)

            
            _, contours, hierarchy = cv2.findContours(mask.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            center = None

            
            #cv2.drawContours(frame, contours, -1, (0,255,255), 5)

            # only proceed if at least one contour was found
            if len(contours) > 0:
                    
                    # find the largest contour in the mask, then use
                    # it to compute the minimum enclosing circle and
                    # centroid
                    contour = max(contours, key=cv2.contourArea)
                    #draw the largest contour
                    cv2.drawContours(frame, [contour], 0, (128,255,0), 2, maxLevel = 0)

                    
                    ((x, y), radius) = cv2.minEnclosingCircle(contour)
                    #center = (int(x),int(y))
                    #radius = int(radius)
                    #cv2.circle(frame,center,radius,(0,255,0),2)
                    
                    
                    if(radius > 15):
                            M = cv2.moments(contour)
                            if(M["m00"] == 0 ):
                                M["m00"] = 0.01
                            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                            
                            cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
                            cv2.circle(frame, center, 5, (0, 0, 255), -1)
                            pts.append(center)
                    else:
                        pts.append((0,0))

                    '''
                    # only proceed if the radius meets a minimum size
                    if radius > 10:
                            # draw the circle and centroid on the frame,
                            # then update the list of tracked points
                            cv2.circle(frame, (int(x), int(y)), int(radius),
                                    (0, 255, 255), 2)
                            cv2.circle(frame, center, 5, (0, 0, 255), -1)
                            pts.appendleft(center)
                    '''

                    '''
                    rect = cv2.minAreaRect(contour)
                    box = cv2.boxPoints(rect)
                    box = np.int0(box)
                    cv2.drawContours(frame,[box],0,(0,0,255),2)
                    '''
            else:
                pts.append((0,0))
                
        cv2.putText(frame, str(counter), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 255), 3)
        counter += 1

        # show screen capture and mask
        cv2.imshow("screen capture", frame)
        cv2.imshow("mask", mask)


        if(len(pts) > 1):

                print("---------")

                chars = ['a', 's', 'j', 'k', 'l']


                # aa = 460
                # sleepTime = 0.1
                # if toggle:

                #     for i in range(0, len(pts)):
                #         print("a")
                #         #if()

                #         # if(pts[4][1] > aa):
                #         #     print("e")
                #         #     keyboard.press('l')
                #         #     sleep(sleepTime)
                #         #     keyboard.release('l')
                #         #     toggle2 = True


                aa = 550
                sleepTime = 0.005
                if toggle:
                    if(pts[0][1] > aa):
                        print("a")
                        keyboard.press('a')
                        time.sleep(sleepTime)
                        keyboard.release('a')
                        toggle2 = True
                    if(pts[1][1] > aa):
                        print("b")
                        keyboard.press('s')
                        time.sleep(sleepTime)
                        keyboard.release('s')
                        toggle2 = True
                    if(pts[2][1] > aa):
                        print("c")
                        keyboard.press('j')
                        time.sleep(sleepTime)
                        keyboard.release('j')
                        toggle2 = True
                    if(pts[3][1] > aa):
                        print("d")
                        keyboard.press('k')
                        time.sleep(sleepTime)
                        keyboard.release('k')
                        toggle2 = True
                    if(pts[4][1] > aa):
                        print("e")
                        keyboard.press('l')
                        time.sleep(sleepTime)
                        keyboard.release('l')
                        toggle2 = True




        
        cv2.waitKey(10)

        # global quit
        if win32api.GetAsyncKeyState(ord('U')):
                break
        
        if win32api.GetAsyncKeyState(ord('G')):
                diff = time.clock() - timeSinceLastToggle
                if(diff > 0.5):
                        timeSinceLastToggle = time.clock()
                        toggle = not toggle


        # diff2 = time.clock() - timeSinceLastKey
        # if(diff2 > 0.0005):
        #         timeSinceLastKey = time.clock()
        #         toggle2 = False
        
        '''
        key = cv2.waitKey(1)
        # if the 'q' key is pressed, stop the loop
        if key == ord("q"):
                break
        '''
        
        end = time.clock()
        
        diffInSeconds = end - start
        diffInMilliSeconds = diffInSeconds*1000
        FPS = 1000 / diffInMilliSeconds
        #print(diffInMilliSeconds)
        

# close any open windows
cv2.destroyAllWindows()
