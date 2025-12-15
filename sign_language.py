import cv2
import time
import HandTrackingModule2 as htm

# ---------------- SETTINGS ----------------
wCam, hCam = 640, 480
SAVE_TIME = 1.0   # seconds to confirm a letter

# -----------------------------------------
cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

detector = htm.handDetector(maxHands=1)

# Finger pattern format:
# [Thumb, Index, Middle, Ring, Pinky]
ALPHABET = {
    (0,1,0,0,0): "A",
    (0,1,1,0,0): "B",
    (0,1,1,1,0): "C",
    (0,1,1,1,1): "D",
    (0,0,1,0,0): "E",
    (0,0,1,1,0): "F",
    (0,0,1,1,1): "G",
    (0,0,0,1,0): "H",
    (0,0,0,1,1): "I",
    (0,0,0,0,1): "J",

    (1,1,0,0,0): "K",
    (1,1,1,0,0): "L",
    (1,1,1,1,0): "M",
    (1,1,1,1,1): "N",
    (1,0,1,0,0): "O",
    (1,0,1,1,0): "P",
    (1,0,1,1,1): "Q",
    (1,0,0,1,0): "R",
    (1,0,0,1,1): "S",
    (1,0,0,0,1): "T",

    (0,1,0,1,0): "U",
    (0,1,0,1,1): "V",
    (0,1,0,0,1): "W",
    (1,1,0,1,0): "X",
    (1,1,0,1,1): "Y",
    (1,1,0,0,1): "Z",

    (0,0,0,0,0): " "   # Fist = Space
}

text = ""
last_pattern = None
pattern_start = None
current_letter = "-"

pTime = 0

# ---------------- MAIN LOOP ----------------
while True:
    success, img = cap.read()
    if not success:
        break

    img = detector.findHands(img)
    lmList, _ = detector.findPosition(img)

    if lmList:
        fingers = detector.fingersUp()
        fingers = (fingers + [0]*5)[:5]
        pattern = tuple(fingers)

        if pattern == last_pattern:
            if pattern_start and time.time() - pattern_start >= SAVE_TIME:
                if pattern in ALPHABET:
                    letter = ALPHABET[pattern]
                    text += letter
                    current_letter = letter
                pattern_start = None
                last_pattern = None
        else:
            last_pattern = pattern
            pattern_start = time.time()
    else:
        last_pattern = None
        pattern_start = None

    # FPS
    cTime = time.time()
    fps = int(1 / (cTime - pTime)) if cTime != pTime else 0
    pTime = cTime

    # UI
    cv2.putText(img, f"FPS: {fps}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

    cv2.putText(img, f"Saved Letter: {current_letter}", (10, 70),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,0,0), 2)

    cv2.putText(img, f"Text: {text[-30:]}", (10, 110),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255), 2)

    cv2.putText(img, "Hold gesture 1 sec to save", (10, hCam-40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200,200,200), 2)

    cv2.putText(img, "C: Clear | Q: Quit", (10, hCam-10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200,200,200), 2)

    cv2.imshow("Sign Language Typing (Easy)", img)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    if key == ord('c'):
        text = ""

cap.release()
cv2.destroyAllWindows()
