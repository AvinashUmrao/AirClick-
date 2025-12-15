import cv2
import mediapipe as mp

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

cap = None  # Delay webcam start until game runs

def gesture_recognition_function():
    """Analyze camera feed and return control signals based on hand gestures."""
    global cap
    if cap is None:
        cap = cv2.VideoCapture(0)

    control = {"left": False, "right": False, "fire": False}

    ret, frame = cap.read()
    if not ret:
        return control

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, handLms, mp_hands.HAND_CONNECTIONS)

            landmarks = handLms.landmark
            index_finger = landmarks[8]
            thumb = landmarks[4]

            if index_finger.x < 0.4:
                control["left"] = True
                cv2.putText(frame, "LEFT!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            elif index_finger.x > 0.6:
                control["right"] = True
                cv2.putText(frame, "RIGHT!", (frame.shape[1] - 200, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            if abs(thumb.x - index_finger.x) < 0.05 and abs(thumb.y - index_finger.y) < 0.05:
                control["fire"] = True
                cv2.putText(frame, "FIRE!", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    cv2.imshow("Hand Detection", frame)
    cv2.moveWindow("Hand Detection", 30, 250)
    cv2.waitKey(1)

    return control

def release_camera():
    global cap
    if cap:
        cap.release()
    try:
        cv2.destroyAllWindows()
    except:
        pass
