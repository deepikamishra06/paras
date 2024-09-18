#!/usr/bin/env python
import os
import cv2
import numpy as np
from picamera2 import Picamera2
import time
from gpiozero import LED
import face_recognition
import csv
from datetime import datetime
import joblib
from threading import Thread
from queue import Queue


RED_LED_PIN = 17    
GREEN_LED_PIN = 16   
YELLOW_LED_PIN = 5  


IMAGE_OUTPUT_DIR = "/home/raspi4/paras/output_database/output_images" 
CSV_FILE = "/home/raspi4/paras/output_database/attendance.csv"
CASCADE_PATH = "/home/raspi4/paras/library/haarcascade_frontalface.xml"  
ENCODINGS_FILE = '/home/raspi4/paras/tools/image_database.joblib' 

green_led = LED(GREEN_LED_PIN)
red_led = LED(RED_LED_PIN)
yellow_led = LED(YELLOW_LED_PIN)

def load_known_faces():
    try:
        encodings_data = joblib.load(ENCODINGS_FILE)
        known_face_encodings = []
        known_face_names = []

        for data in encodings_data:
            known_face_encodings.append(data['encoding'])
            known_face_names.append(data['name'])

    except Exception as e:
        return [], []

    return known_face_encodings, known_face_names

def detect_faces(image):
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_image)
    return face_locations

def compare_faces(known_face_encodings, known_face_names, detected_encoding, threshold=0.60):
    face_distances = face_recognition.face_distance(known_face_encodings, detected_encoding)
    best_match_index = np.argmin(face_distances)
    similarity = 1 - face_distances[best_match_index]

    if similarity > threshold:
        return known_face_names[best_match_index], similarity
    else:
        return "Unknown", 0

def save_image(image, name, timestamp):
    filename = f"{name}_{timestamp}.jpg"
    filepath = os.path.join(IMAGE_OUTPUT_DIR, filename)
    cv2.imwrite(filepath, image, [int(cv2.IMWRITE_JPEG_QUALITY), 90])

def write_to_csv(name, timestamp, similarity):
    with open(CSV_FILE, mode='a', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow([name, timestamp, f"{similarity:.4f}"])

def handle_detection(image, name, similarity):
    if name == "Unknown":
        return  # Skip saving and logging for unknown faces
    entry_time = datetime.now().strftime('%d_%m_%H_%M_%S')
    detection_queue.put((image, name, entry_time, similarity))

def process_detections():
    while True:
        image, name, timestamp, similarity = detection_queue.get()
        save_image(image, name, timestamp)
        write_to_csv(name, timestamp, similarity)
        detection_queue.task_done()

def handle_led(led, duration):
    led.on()
    time.sleep(duration)
    led.off()

def main():
    global detection_queue
    detection_queue = Queue()

    Thread(target=process_detections, daemon=True).start()

    known_face_encodings, known_face_names = load_known_faces()

    camera = Picamera2()
    config = camera.create_preview_configuration({"size": (320, 240), "format": "RGB888"})  # Reduced resolution
    camera.configure(config)
    camera.start(show_preview=False)
    camera.set_controls({"FrameRate": 60})
    time.sleep(1)  # Allow camera to warm up

    # Yellow LED on when camera is active
    yellow_led.on()

    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, mode='a', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(["Name", "Timestamp", "Similarity"])

    last_modified_time = os.path.getmtime(ENCODINGS_FILE)
    
    while True:
        current_modified_time = os.path.getmtime(ENCODINGS_FILE)
        if current_modified_time != last_modified_time:
            known_face_encodings, known_face_names = load_known_faces()
            last_modified_time = current_modified_time

        image = camera.capture_array('main')
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        face_locations = detect_faces(rgb_image)
        face_encodings = face_recognition.face_encodings(rgb_image, face_locations)

        if len(face_locations) == 0:
            continue

        for face_encoding, (top, right, bottom, left) in zip(face_encodings, face_locations):
            name, similarity = compare_faces(known_face_encodings, known_face_names, face_encoding)
            
            if name == "Unknown":
                handle_led(red_led, 2)
            else:
                handle_led(green_led, 2)

            handle_detection(image, name, similarity)
            cv2.rectangle(image, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(image, f"{name} ({similarity:.2f})", (left, top - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            cv2.imshow("Hotel Face Recognition", image)
            cv2.waitKey(1)  # Allow the window to render

            time.sleep(1)  # Wait for 2 seconds before processing the next frame

    camera.close()
    yellow_led.off()

if __name__ == "__main__":
    main()

