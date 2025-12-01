
import face_recognition
import os
import pickle
import sys

dataset_folder = "dataset"
encodings_file = "encodings.pickle"

known_encodings = []
known_names = []

print("Starting face encoding process...")

# Load existing encodings if available
if os.path.exists(encodings_file):
    try:
        with open(encodings_file, "rb") as f:
            data = pickle.load(f)
            known_encodings = data["encodings"]
            known_names = data["names"]
        print(f"✓ Loaded {len(known_encodings)} existing encodings")
    except Exception as e:
        print(f"Warning: Could not load existing encodings: {e}")
        known_encodings = []
        known_names = []

# Check if dataset folder exists
if not os.path.exists(dataset_folder):
    print(f"✗ Error: {dataset_folder} folder not found!")
    sys.exit(1)

# Loop through each user folder
processed = 0
failed = 0

for user in os.listdir(dataset_folder):
    user_path = os.path.join(dataset_folder, user)
    if not os.path.isdir(user_path):
        continue

    # Load the user's face image
    img_path = os.path.join(user_path, f"{user}.jpg")
    
    if not os.path.exists(img_path):
        print(f"✗ Image not found for user: {user}")
        failed += 1
        continue
    
    try:
        print(f"Processing {user}...")
        
        # Load image
        image = face_recognition.load_image_file(img_path)
        print(f"  - Image loaded: {image.shape}")
        
        # Find face encodings
        face_encodings = face_recognition.face_encodings(image)
        
        if len(face_encodings) == 0:
            print(f"  ✗ No face detected in image for {user}")
            failed += 1
            continue
        
        if len(face_encodings) > 1:
            print(f"  ⚠ Warning: Multiple faces detected, using first one")
        
        encoding = face_encodings[0]
        
        # Check if user already exists
        if user in known_names:
            # Update existing encoding
            idx = known_names.index(user)
            known_encodings[idx] = encoding
            print(f"  ✓ Updated encoding for {user}")
        else:
            # Add new encoding
            known_encodings.append(encoding)
            known_names.append(user)
            print(f"  ✓ Added new encoding for {user}")
        
        processed += 1
        
    except Exception as e:
        print(f"  ✗ Error processing {user}: {e}")
        import traceback
        traceback.print_exc()
        failed += 1

# Save updated encodings
if processed > 0:
    try:
        data = {"encodings": known_encodings, "names": known_names}
        with open(encodings_file, "wb") as f:
            pickle.dump(data, f)
        print(f"\n✓ Encodings saved to {encodings_file}")
        print(f"  - Total users: {len(known_encodings)}")
        print(f"  - Successfully processed: {processed}")
        if failed > 0:
            print(f"  - Failed: {failed}")
    except Exception as e:
        print(f"\n✗ Error saving encodings: {e}")
        sys.exit(1)
else:
    print("\n✗ No faces were successfully encoded!")
    sys.exit(1)

print("\n✓ Face encoding complete!")