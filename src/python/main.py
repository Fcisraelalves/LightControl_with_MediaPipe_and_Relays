import cv2
import mediapipe as mp
import serial
import time

class FingersTips:
    FINGER_TIPS_IDS = [4, 8, 12, 16, 20]

def get_serial_connection(port : str, baudrate: int):
    serial_connection = serial.Serial(port, baudrate)
    time.sleep(2)
    return serial_connection

cap = cv2.VideoCapture(0)
hand = mp.solutions.hands
hands = hand.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.9)
hand_drawing = mp.solutions.drawing_utils

fingers_tips_ids = FingersTips.FINGER_TIPS_IDS

arduino_connection = get_serial_connection('/dev/ttyACM0', 9600)

while True:
    _, frame = cap.read()
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)
    if results.multi_hand_landmarks and results.multi_handedness:
        for joints, hand_info in zip(results.multi_hand_landmarks, results.multi_handedness):
            label = hand_info.classification[0].label
            hand_drawing.draw_landmarks(frame, joints, hand.HAND_CONNECTIONS)
            points = []
            for lm in joints.landmark:
                h, w, _ = frame.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                points.append((cx, cy))
            raised_fingers = []
            if label == 'Right':
                if points[fingers_tips_ids[0]][0] > points[fingers_tips_ids[0] - 1][0]:
                    raised_fingers.append(0)
                else:
                    raised_fingers.append(1)
            else:
                if points[fingers_tips_ids[0]][0] < points[fingers_tips_ids[0] - 1][0]:
                    raised_fingers.append(0)
                else:
                    raised_fingers.append(1)
            for id in range(1, 5):
                if points[fingers_tips_ids[id]][1] < points[fingers_tips_ids[id] - 2][1]:
                    raised_fingers.append(1)
                else:
                    raised_fingers.append(0)

            arduino_connection.write(("".join(map(str, raised_fingers)) + "\n").encode())

            text = f'{label}: {raised_fingers}'
            cv2.putText(frame, text, (10,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (208, 224, 64), 1)
    else:
        arduino_connection.write(b"00000\n")
    cv2.imshow('Hand Detector', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

arduino_connection.close()
cap.release()
cv2.destroyAllWindows()

