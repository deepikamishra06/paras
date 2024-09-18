##!/usr/bin/env python
#import os
#import cv2
#import numpy as np
#from picamera2 import Picamera2
#import time
#from gpiozero import LED
#import face_recognition
#import csv
#from datetime import datetime
#import joblib
#from threading import Thread
#from queue import Queue
#
#os.environ['LD_PRELOAD'] = '/usr/lib/arm-linux-gnueabihf/libatomic.so.1.2.0'
#
#CASCADE_PATH = "/home/raspi4/ansalgolflink2/library/haarcascade_frontalface.xml"  # Path to Haar Cascade classifier
#LED_PIN = 16  # GPIO pin number for the LED
#CSV_FILE = "/home/raspi4/ansalgolflink2/tools/nosync/Ansal_golf_link_2_entrysheet.csv"
#IMAGE_OUTPUT_DIR = "/home/raspi4/ansalgolflink2/outdb/output_images"  # Directory to save detected face images
#ENCODINGS_FILE = '/home/raspi4/ansalgolflink2/tools/ansalgolflink_imagedb.joblib'  # Path to the saved face encodings file
#
## Initialize LED
#led = LED(LED_PIN)
#
#def load_known_faces():
#    try:
#        encodings_data = joblib.load(ENCODINGS_FILE)
#        known_face_encodings = []
#        known_face_names = []
#
#        for data in encodings_data:
#            known_face_encodings.append(data['encoding'])
#            known_face_names.append(data['name'])
#
#        # Verify all encodings are of shape (128,)
#        for i, encoding in enumerate(known_face_encodings):
#            if encoding.shape != (128,):
#                print(f"Warning: Encoding {i} has unexpected shape {encoding.shape}")
#
#    except Exception as e:
#        print(f"Error loading encodings: {e}")
#        return [], []
#
#    return known_face_encodings, known_face_names
#
#def detect_faces(image):
#    # Convert the image to RGB format
#    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
#
#    # Use face_recognition.face_locations for face detection
#    face_locations = face_recognition.face_locations(rgb_image)
#    return face_locations
#
#def compare_faces(known_face_encodings, known_face_names, detected_encoding, threshold=0.5):
#    if not known_face_encodings:
#        return "Unknown", 0
#
#    face_distances = face_recognition.face_distance(known_face_encodings, detected_encoding)
#    best_match_index = np.argmin(face_distances)
#    similarity = 1 - face_distances[best_match_index]
#
#    if similarity > threshold:
#        return known_face_names[best_match_index], similarity
#    else:
#        return "Unknown", 0
#
#def save_image(image, name, timestamp):
#    filename = f"{name}_{timestamp}.jpg"
#    filepath = os.path.join(IMAGE_OUTPUT_DIR, filename)
#    cv2.imwrite(filepath, image, [int(cv2.IMWRITE_JPEG_QUALITY), 90])  # Save with JPEG format and high compression
#    print(f"Image saved: {filename}")
#    return filename
#
#def write_to_csv(name, timestamp, similarity):
#    with open(CSV_FILE, mode='a', newline='') as csv_file:
#        csv_writer = csv.writer(csv_file)
#        csv_writer.writerow([name, timestamp, f"{similarity:.4f}"])
#
#def handle_detection(image, name, similarity):
#    entry_time = datetime.now().strftime('%d_%m_%H_%M_%S')
#    detection_queue.put((image, name, entry_time, similarity))
#
#def process_detections():
#    while True:
#        image, name, timestamp, similarity = detection_queue.get()
#        try:
#            image_name = save_image(image, name, timestamp)
#            write_to_csv(name, timestamp, similarity)
#        
#            # If the face is unknown, save it as a known face
#            if name == "Unknown":
#                new_face_image = cv2.imread(os.path.join(IMAGE_OUTPUT_DIR, image_name))
#                rgb_new_face_image = cv2.cvtColor(new_face_image, cv2.COLOR_BGR2RGB)
#                new_face_encoding = face_recognition.face_encodings(rgb_new_face_image)[0]
#                add_new_face_encoding(image_name.split('.')[0], new_face_encoding)
#        
#        except Exception as e:
#            print(f"Error processing detection: {e}")
#        finally:
#            detection_queue.task_done()
#
#def add_new_face_encoding(name, encoding):
#    try:
#        encodings_data = joblib.load(ENCODINGS_FILE)
#        encodings_data.append({'name': name, 'encoding': encoding})
#        joblib.dump(encodings_data, ENCODINGS_FILE)
#        print(f"Added new face encoding for {name}")
#    except Exception as e:
#        print(f"Error adding new face encoding: {e}")
#
#def handle_led():
#    led.on()
#    time.sleep(2)  # LED ON time for 2 seconds
#    led.off()
#
#def main():
#    global detection_queue
#    detection_queue = Queue()
#
#    # Start a thread to process detections from the queue
#    Thread(target=process_detections, daemon=True).start()
#
#    # Initialize the camera and capture frames
#    camera = Picamera2()
#    config = camera.create_preview_configuration({"size": (840, 700), "format": "RGB888"})  # Reduced resolution
#    camera.configure(config)
#    camera.start(show_preview=False)
#    camera.set_controls({"FrameRate": 60})  # Increase the frame rate to 60 FPS
#    # Allow the camera to warm up
#    time.sleep(2)
#
#    known_face_encodings, known_face_names = load_known_faces()
#    print("Known Faces:", known_face_names)
#
#    # Create or open the CSV file and write the header if the file is new
#    if not os.path.exists(CSV_FILE):
#        with open(CSV_FILE, mode='a', newline='') as csv_file:
#            csv_writer = csv.writer(csv_file)
#            csv_writer.writerow(["Name", "Timestamp", "Similarity"])
#
#    last_detection_time = time.time() - 5  # Initialize with a time before 5 seconds ago
#    last_modified_time = os.path.getmtime(ENCODINGS_FILE)  # Get the last modified time of the encodings file
#
#    while True:
#        try:
#            # Check if the encodings file has been modified
#            current_modified_time = os.path.getmtime(ENCODINGS_FILE)
#            if current_modified_time != last_modified_time:
#                known_face_encodings, known_face_names = load_known_faces()
#                last_modified_time = current_modified_time
#                print("Reloaded known faces from encodings file.")
#
#            # Get the NumPy array representation of the frame
#            image = camera.capture_array('main')
#
#            # Convert the image to RGB format
#            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
#
#            # Detect faces
#            face_locations = detect_faces(rgb_image)
#
#            # Encode the detected faces
#            face_encodings = face_recognition.face_encodings(rgb_image, face_locations)
#
#            # Compare faces and get name and similarity
#            for face_encoding, (top, right, bottom, left) in zip(face_encodings, face_locations):
#                name, similarity = compare_faces(known_face_encodings, known_face_names, face_encoding)
#                print("Detected Face:", name, similarity)
#
#                # Control the LED to glow for 2 seconds
#                current_time = time.time()
#                if current_time - last_detection_time >= 5:
#                    Thread(target=handle_led).start()
#
#                    # Handle the detection asynchronously using the queue
#                    handle_detection(image, name, similarity)
#
#                    last_detection_time = current_time
#
#                # Draw rectangle around detected face
#                cv2.rectangle(image, (left, top), (right, bottom), (0, 255, 0), 2)
#                cv2.putText(image, f"{name} ({similarity:.2f})", (left, top - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
#
#            # Show the frame with the result
#            cv2.imshow("Ansal Golf Link-1 Face Recognition Known_Unknown_Both", image)
#            cv2.waitKey(1)  # Add this line to give the window time to render
#
#        except Exception as e:
#            print(f"Error in main loop: {e}")
#
#    # Release the camera
#    camera.close()
#
#if __name__ == "__main__":
#    main()


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

#os.environ['LD_PRELOAD'] = '/usr/lib/arm-linux-gnueabihf/libatomic.so.1.2.0'

LED_PIN = 16  # GPIO pin number for the LED
IMAGE_OUTPUT_DIR = "/home/raspi4/paras/output_database/output_images" 
CSV_FILE = "/home/raspi4/paras/output_database/attendance.csv"
CASCADE_PATH = "/home/raspi4/paras/library/haarcascade_frontalface.xml"  
ENCODINGS_FILE = '/home/raspi4/paras/tools/image_database.joblib'
# Initialize LED
led = LED(LED_PIN)

def load_known_faces():
    try:
        encodings_data = joblib.load(ENCODINGS_FILE)
        known_face_encodings = []
        known_face_names = []

        for data in encodings_data:
            known_face_encodings.append(data['encoding'])
            known_face_names.append(data['name'])

        # Verify all encodings are of shape (128,)
        for i, encoding in enumerate(known_face_encodings):
            if encoding.shape != (128,):
                print(f"Warning: Encoding {i} has unexpected shape {encoding.shape}")

    except Exception as e:
        print(f"Error loading encodings: {e}")
        return [], []

    return known_face_encodings, known_face_names

def detect_faces(image):
    # Convert the image to RGB format
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Use face_recognition.face_locations for face detection
    face_locations = face_recognition.face_locations(rgb_image)
    return face_locations

def compare_faces(known_face_encodings, known_face_names, detected_encoding, threshold=0.5):
    if not known_face_encodings:
        return "Unknown", 0

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
    cv2.imwrite(filepath, image, [int(cv2.IMWRITE_JPEG_QUALITY), 90])  # Save with JPEG format and high compression
    print(f"Image saved: {filename}")
    return filename

def write_to_csv(name, timestamp, similarity):
    with open(CSV_FILE, mode='a', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow([name, timestamp, f"{similarity:.4f}"])

def handle_detection(image, name, similarity):
    entry_time = datetime.now().strftime('%d_%m_%H_%M_%S')
    detection_queue.put((image, name, entry_time, similarity))

def process_detections():
    while True:
        image, name, timestamp, similarity = detection_queue.get()
        try:
            image_name = save_image(image, name, timestamp)
            write_to_csv(name, timestamp, similarity)
        
            # If the face is unknown, save it as a known face
            if name == "Unknown":
                new_face_image = cv2.imread(os.path.join(IMAGE_OUTPUT_DIR, image_name))
                rgb_new_face_image = cv2.cvtColor(new_face_image, cv2.COLOR_BGR2RGB)
                new_face_encoding = face_recognition.face_encodings(rgb_new_face_image)[0]
                add_new_face_encoding(image_name.split('.')[0], new_face_encoding)
        
        except Exception as e:
            print(f"Error processing detection: {e}")
        finally:
            detection_queue.task_done()

def add_new_face_encoding(name, encoding):
    try:
        encodings_data = joblib.load(ENCODINGS_FILE)
        encodings_data.append({'name': name, 'encoding': encoding})
        joblib.dump(encodings_data, ENCODINGS_FILE)
        print(f"Added new face encoding for {name}")
    except Exception as e:
        print(f"Error adding new face encoding: {e}")

def handle_led():
    led.on()
    time.sleep(3)  # LED ON time for 0.5 seconds
    led.off()

def main():
    global detection_queue
    detection_queue = Queue()

    # Start a thread to process detections from the queue
    Thread(target=process_detections, daemon=True).start()

    # Initialize the camera and capture frames
    camera = Picamera2()
    config = camera.create_preview_configuration({"size": (840, 700), "format": "RGB888"})  # Reduced resolution
    camera.configure(config)
    camera.start(show_preview=False)
    camera.set_controls({"FrameRate": 60})  # Increase the frame rate to 60 FPS
    # Allow the camera to warm up
    time.sleep(2)

    known_face_encodings, known_face_names = load_known_faces()
    print("Known Faces:", known_face_names)

    # Create or open the CSV file and write the header if the file is new
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, mode='a', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(["Name", "Timestamp", "Similarity"])

    last_detection_time = time.time() - 5  # Initialize with a time before 5 seconds ago
    last_modified_time = os.path.getmtime(ENCODINGS_FILE)  # Get the last modified time of the encodings file

    while True:
        try:
            # Check if the encodings file has been modified
            current_modified_time = os.path.getmtime(ENCODINGS_FILE)
            if current_modified_time != last_modified_time:
                known_face_encodings, known_face_names = load_known_faces()
                last_modified_time = current_modified_time
                print("Reloaded known faces from encodings file.")

            # Get the NumPy array representation of the frame
            image = camera.capture_array('main')

            # Convert the image to RGB format
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            # Detect faces
            face_locations = detect_faces(rgb_image)

            # Encode the detected faces
            face_encodings = face_recognition.face_encodings(rgb_image, face_locations)

            # Compare faces and get name and similarity
            for face_encoding, (top, right, bottom, left) in zip(face_encodings, face_locations):
                name, similarity = compare_faces(known_face_encodings, known_face_names, face_encoding)
                print("Detected Face:", name, similarity)

                # Blink LED if a known face is detected
                if name != "Unknown":
                    Thread(target=handle_led).start()

                # Handle the detection asynchronously using the queue
                handle_detection(image, name, similarity)

                # Draw rectangle around detected face
                cv2.rectangle(image, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(image, f"{name} ({similarity:.2f})", (left, top - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            # Show the frame with the result
            cv2.imshow("Ansal Golf Link-1 Face Recognition Known_Unknown_Both", image)
            cv2.waitKey(1)  # Add this line to give the window time to render

        except Exception as e:
            print(f"Error in main loop: {e}")

    # Release the camera
    camera.close()

if __name__ == "__main__":
    main()

































