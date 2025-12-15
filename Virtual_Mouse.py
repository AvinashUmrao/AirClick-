import os
# Suppress MediaPipe and TensorFlow logs
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Suppress TensorFlow logs
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'  # Suppress oneDNN logs
os.environ['TF_CPP_MIN_VLOG_LEVEL'] = '3'  # Suppress verbose logging

# Suppress Pygame welcome message
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

import cv2
import numpy as np
import HandTrackingModule2 as htm
import time
import subprocess
import os
import sys
from pynput.mouse import Controller, Button

# Suppress MediaPipe and TensorFlow warnings
import warnings
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=FutureWarning)

##########################
wCam, hCam = 640, 480
frameR = 100  # Border size for control zone
smoothening = 7

launch_hold_time = 1.5  # seconds to hold fist to launch app
dragging = False
left_click_active = False
##########################

pTime = 0
plocX, plocY = 0, 0
clocX, clocY = 0, 0
fist_start = None
open_palm_start = None
sign_start = None

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

detector = htm.handDetector(maxHands=1)
mouse = Controller()
screen_width, screen_height = 1920, 1080  # You can dynamically fetch if needed

base_dir = os.path.dirname(os.path.abspath(__file__))
space_script = os.path.join(base_dir, "main.py")   # Space shooter game
sign_script = os.path.join(base_dir, "sign_language.py")  # Hand sign language recognizer

while True:
    success, img = cap.read()
    img = detector.findHands(img)
    lmList, bbox = detector.findPosition(img)

    if len(lmList) != 0:
        # try:
            x1, y1 = lmList[8][1:]   # Index tip
            x2, y2 = lmList[12][1:]  # Middle tip
            x3, y3 = lmList[16][1:]  # Ring tip
            x4, y4 = lmList[4][1:]   # Thumb tip
            x5, y5 = lmList[20][1:]  # Pinky tip

            fingers = detector.fingersUp()
            fingers = (fingers + [0]*5)[:5]  # Ensure length is 5
            totalFingers = sum(fingers)

            rect_width = wCam - 2 * frameR
            rect_height = hCam - 2 * frameR
            x1_rect = frameR
            y1_rect = frameR
            x2_rect = wCam - frameR
            y2_rect = hCam - frameR

            cv2.rectangle(img, (x1_rect, y1_rect), (x2_rect, y2_rect), (255, 0, 255), 2)

            # Moving Mode (Only Index Up)
            if fingers == [0, 1, 0, 0, 0]:
                x3_ = np.interp(x1, (x1_rect, x2_rect), (0, screen_width))
                y3_ = np.interp(y1, (y1_rect, y2_rect), (0, screen_height))

                clocX = plocX + (x3_ - plocX) / smoothening
                clocY = plocY + (y3_ - plocY) / smoothening

                if fingers[4] == 1:
                    if not dragging:
                        mouse.press(Button.left)
                        dragging = True
                else:
                    if dragging:
                        mouse.release(Button.left)
                        dragging = False

                mouse.position = (screen_width - clocX, clocY)
                cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
                plocX, plocY = clocX, clocY

            # Left Click (Index + Middle) - single click per pinch
            elif fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 0:
                length, img, lineInfo = detector.findDistance(8, 12, img)
                if length < 40 and not left_click_active:
                    cv2.circle(img, (lineInfo[4], lineInfo[5]), 15, (0, 255, 0), cv2.FILLED)
                    mouse.click(Button.left)
                    left_click_active = True
                elif length >= 40:
                    left_click_active = False

            # Right Click (Index + Middle + Ring only)
            elif fingers == [0, 1, 1, 1, 0]:
                mouse.click(Button.right)
                time.sleep(0.3)

            # Scroll Up (Only Thumb)
            elif fingers == [1, 0, 0, 0, 0]:
                mouse.scroll(0, 2)
                time.sleep(0.2)

            # Scroll Down (Only Pinky)
            elif fingers == [0, 0, 0, 0, 1]:
                mouse.scroll(0, -2)
                time.sleep(0.2)

            # Open Palm Gesture (all 5 fingers) to Launch Space Shooter Game
            if totalFingers == 5:
                if open_palm_start is None:
                    open_palm_start = time.time()
                elif time.time() - open_palm_start >= launch_hold_time:
                    print("[INFO] Launching Space Shooter Game...")
                    cap.release()
                    cv2.destroyAllWindows()
                    subprocess.run([sys.executable, space_script])
                    cap = cv2.VideoCapture(0)
                    cap.set(3, wCam)
                    cap.set(4, hCam)
                    fist_start = None
                    open_palm_start = None
                    sign_start = None
                    continue
            else:
                open_palm_start = None

            # Index + Pinky Up (others down) to Launch Sign Language Recognizer
            if fingers == [0, 1, 0, 0, 1]:
                if sign_start is None:
                    sign_start = time.time()
                elif time.time() - sign_start >= launch_hold_time:
                    print("[INFO] Launching Hand Sign Language Recognizer...")
                    cap.release()
                    cv2.destroyAllWindows()
                    subprocess.run([sys.executable, sign_script])
                    cap = cv2.VideoCapture(0)
                    cap.set(3, wCam)
                    cap.set(4, hCam)
                    fist_start = None
                    open_palm_start = None
                    sign_start = None
                    continue
            else:
                sign_start = None

        # except Exception as e:
        #     print(f"[ERROR] {e}")

    cTime = time.time()
    fps = 1 / (cTime - pTime) if (cTime - pTime) != 0 else 0
    pTime = cTime
    cv2.putText(img, f'FPS: {int(fps)}', (20, 50),
                cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)

    cv2.imshow("AI Virtual Mouse", img)
    cv2.waitKey(1)

cap.release()