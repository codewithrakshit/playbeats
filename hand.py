import cv2
import mediapipe as mp
import pygame
import math
import os
import time

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils
pygame.mixer.init()

sound_files = {
    "Thumb": "/Users/rakshitkriplani/Desktop/Hand gesture instrument/frontend/sounds/03.mp3",
    "Index": "/Users/rakshitkriplani/Desktop/Hand gesture instrument/frontend/sounds/01.mp3",
    "Middle": "/Users/rakshitkriplani/Desktop/Hand gesture instrument/frontend/sounds/la4-102327.mp3",
    "Ring": "/Users/rakshitkriplani/Desktop/Hand gesture instrument/frontend/sounds/06.mp3",
    "Pinky": "/Users/rakshitkriplani/Desktop/Hand gesture instrument/frontend/sounds/06.mp3"
}

for key, file in sound_files.items():
    if not os.path.exists(file):
        print(f"Warning: Sound file {file} for {key} not found!")

PRESS_THRESHOLD = 40 
PINCH_THRESHOLD = 50  
volume = 0.5  
slider_x, slider_y, slider_length = 50, 150, 200
settings_open = False  
last_pinch_time = 0  
PINCH_COOLDOWN = 1.0

def play_sound(gesture_name):
    if gesture_name in sound_files:
        try:
            sound = pygame.mixer.Sound(sound_files[gesture_name])
            sound.set_volume(volume)
            sound.play()
        except Exception as e:
            print(f"Error playing sound for {gesture_name}: {e}")

def calculate_distance(p1, p2):
    return math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)

def update_volume(index_x):
    global volume
    relative_position = (index_x - slider_x) / slider_length
    volume = max(0.0, min(1.0, relative_position))

def draw_settings(frame):
    global settings_open
    icon_x, icon_y, icon_size = 20, 20, 40
    # Draw settings icon area
    cv2.rectangle(frame, (icon_x, icon_y), (icon_x + icon_size, icon_y + icon_size), (0, 255, 255), -1)
    # Use text as the icon
    cv2.putText(frame, "SET", (icon_x + 5, icon_y + 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

    # Draw volume slider if settings are open
    if settings_open:
        cv2.putText(frame, "Volume", (slider_x, slider_y - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        slider_position = int(slider_x + volume * slider_length)
        cv2.line(frame, (slider_x, slider_y), (slider_x + slider_length, slider_y), (255, 255, 255), 3)
        cv2.circle(frame, (slider_position, slider_y), 8, (0, 255, 0), -1)
    return icon_x, icon_y, icon_size

def toggle_settings_with_pinch(thumb_tip, index_tip):
    global settings_open, last_pinch_time
    current_time = time.time()
    pinch_distance = calculate_distance(thumb_tip, index_tip)
    if pinch_distance < PINCH_THRESHOLD and (current_time - last_pinch_time > PINCH_COOLDOWN):
        settings_open = not settings_open
        last_pinch_time = current_time

cap = cv2.VideoCapture(0)
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame. Exiting...")
        break

    frame = cv2.flip(frame, 1) 
    h, w, _ = frame.shape
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    draw_settings(frame)


    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            landmarks = [(int(lm.x * w), int(lm.y * h)) for lm in hand_landmarks.landmark]
            thumb_tip, index_tip = landmarks[4], landmarks[8]
            palm = landmarks[0]

            toggle_settings_with_pinch(thumb_tip, index_tip)

            if settings_open and slider_x <= index_tip[0] <= slider_x + slider_length:
                update_volume(index_tip[0])
            finger_distances = {
                "Thumb": calculate_distance(landmarks[4], palm),
                "Index": calculate_distance(landmarks[8], palm),
                "Middle": calculate_distance(landmarks[12], palm),
                "Ring": calculate_distance(landmarks[16], palm),
                "Pinky": calculate_distance(landmarks[20], palm),
            }

            for finger, distance in finger_distances.items():
                if distance < PRESS_THRESHOLD:
                    play_sound(finger)

    cv2.imshow("Play Beats - Gesture Instrument", frame)

    if cv2.waitKey(10) & 0xFF == ord('q'):  
        break

cap.release()
cv2.destroyAllWindows()
