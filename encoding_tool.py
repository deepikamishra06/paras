import face_recognition
import joblib
import os
import time

# Paths
dir_a = '/home/raspi4/paras/input_database/Residence_Photos'
dir_b = '/home/raspi4/paras/input_database/House_Help'
dir_c = '/home/raspi4/paras/input_database/Guest_Photos'
face_data_file = '/home/raspi4/paras/tools/image_database.joblib'

# Initialize face data
face_data = []

def encode_faces(image_paths):
    new_face_data = []

    for image_path in image_paths:
        try:
            name = os.path.basename(image_path)
            
            image = face_recognition.load_image_file(image_path)
            encodings = face_recognition.face_encodings(image)
            
            if not encodings:
                print(f"No face found in {image_path}")
                continue
            
            for encoding in encodings:
                if encoding.shape == (128,):
                    new_face_data.append({'name': name, 'encoding': encoding})
                    print(f"Encoded and added {name} to new_face_data.")
                else:
                    print(f"Unexpected encoding shape for {name}: {encoding.shape}")
        
        except Exception as e:
            print(f"Error processing {image_path}: {e}")

    return new_face_data
user_input_mails_rx
def get_image_paths():
    all_dirs = [dir_a, dir_b, dir_c]
    image_paths = []

    for directory in all_dirs:
        for f in os.listdir(directory):
            file_path = os.path.join(directory, f)
            if not os.path.isdir(file_path):
                if os.path.basename(file_path) not in processed_files:
                    image_paths.append(file_path)
                else:
                    print(f"Skipping already processed file: {os.path.basename(file_path)}")

    print(f"Found {len(image_paths)} new images to process.")
    return image_paths

def save_face_data():
    joblib.dump(face_data, face_data_file)
    #print("Face encodings saved successfully!")

# Load existing face data to continue processing new images
if os.path.exists(face_data_file) and os.path.getsize(face_data_file) > 0:
    try:
        face_data = joblib.load(face_data_file)
        print(f"Loaded existing face data with {len(face_data)} records.")
    except EOFError:
        face_data = []
        print("Existing face data file is empty or corrupted, starting fresh.")
else:
    face_data = []
    print("No existing face data file found, starting fresh.")

# Track processed files
processed_files = {data['name'] for data in face_data}
print(f"Initialized processed files set with {len(processed_files)} entries.")

# Create the initial database from existing images
print("Creating the initial database from existing images...")
initial_image_paths = get_image_paths()
new_face_data = encode_faces(initial_image_paths)

if new_face_data:
    face_data.extend(new_face_data)
    save_face_data()
    processed_files.update({data['name'] for data in new_face_data})
    print(f"Added {len(new_face_data)} new face encodings.")
else:
    print("No face encodings found in existing images.")

# Continuous loop for processing new images
while True:
    print("Checking for new images...")
    image_paths = get_image_paths()
    new_face_data = encode_faces(image_paths)

    if new_face_data:
        face_data.extend(new_face_data)
        save_face_data()
        processed_files.update({data['name'] for data in new_face_data})
        print(f"Added {len(new_face_data)} new face encodings.")
    else:
        print("No new face encodings found.")

    # Sleep for a while before checking for new images again
    time.sleep(10)  # Check every 10 seconds

