import cv2
import mediapipe as mp
import time
import math
import numpy as np
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
#volume.GetMute()
#volume.GetMasterVolumeLevel()
volRange = volume.GetVolumeRange()
volume.SetMasterVolumeLevel(-20.0, None)

minVol = volRange[0]
maxVol = volRange[1]

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

mpHands = mp.solutions.hands
hands = mpHands.Hands(static_image_mode=False,
                      max_num_hands=2,
                      min_detection_confidence=0.7,
                      min_tracking_confidence=0.7)
mpDraw = mp.solutions.drawing_utils

pTime = 0
cTime = 0

list_hands = []
x1 = 0
x2 = 0
y1 = 0
y2 = 0

while True:
    success,img = cap.read()
    #img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
    img = cv2.flip(img,1)
    results = hands.process(img)

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            for id,lm in enumerate(handLms.landmark):
                #print(id,lm)
                h,w,c = img.shape
                cx, cy = int(lm.x*w), int(lm.y*h)

                #print(id,cx,cy)
                if( id == 4): # first landmark -> 0
                    cv2.circle(img,(cx,cy),10,(255,0,255),cv2.FILLED)
                    x1,y1 = cx,cy
                if (id == 8):  # first landmark -> 0
                    cv2.circle(img, (cx, cy), 10, (255, 0, 255), cv2.FILLED)
                    x2,y2 = cx,cy

                cv2.line(img,(x1,y1),(x2,y2),(255,0,255),3,3)
                dx = (x1+x2)//2
                dy = (y1+y2)//2
                cv2.circle(img, (dx, dy), 10, (0, 255, 255), cv2.FILLED)

                len = math.hypot(x2-x1,y2-y1)
                 # hand range 15 to 170
                 # vol range -65 to 0
                 # to convert hand range to vol range we use np.interp()
                vol = np.interp(len,[15,170],[minVol,maxVol])
                volume.SetMasterVolumeLevel(vol, None)
                print(len,vol)



            mpDraw.draw_landmarks(img,handLms,mpHands.HAND_CONNECTIONS)

    cTime = time.time()
    fps = 1/(cTime-pTime)
    pTime = cTime
    cv2.putText(img,str(int(fps)),(10,70),cv2.FONT_HERSHEY_PLAIN,3,(255,0,255),3)

    cv2.imshow('Image',img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
