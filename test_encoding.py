#!/usr/bin/env python3
"""
Test script to verify face encoding works
"""

import face_recognition
import os
import sys
import pickle

def test_encoding():
    print("\n=== Testing Face Encoding ===\n")
    
    # Check if dataset folder exists
    if not os.path.exists("dataset"):
        print("✗ dataset/ folder not found!")
        return False
    
    # Find user folders
    users = [d for d in os.listdir("dataset") if os.path.isdir(os.path.join("dataset", d))]
    
    if not users:
        print("✗ No user folders found in dataset/")
        print("Please run signup first to capture a face")
        return False
    
    print(f"Found {len(users)} user folder(s): {users}\n")
    
    all_encodings = []
    all_names = []
    
    for user in users:
        img_path = f"dataset/{user}/{user}.jpg"
        
        if not os.path.exists(img_path):
            print(f"✗ Image not found: {img_path}")
            continue
        
        print(f"Testing: {user}")
        print(f"  Image: {img_path}")
        
        try:
            # Load image
            image = face_recognition.load_image_file(img_path)
            print(f"  ✓ Image loaded - Shape: {image.shape}")
            
            # Detect faces
            face_locations = face_recognition.face_locations(image)
            print(f"  ✓ Face locations found: {len(face_locations)}")
            
            if len(face_locations) == 0:
                print(f"  ✗ ERROR: No face detected in image!")
                print(f"  This usually means:")
                print(f"    - Image is too small")
                print(f"    - Face is not clearly visible")
                print(f"    - Image is corrupted")
                continue
            
            # Encode faces
            encodings = face_recognition.face_encodings(image, face_locations)
            print(f"  ✓ Face encodings generated: {len(encodings)}")
            
            if len(encodings) > 0:
                print(f"  ✓ Encoding shape: {encodings[0].shape}")
                all_encodings.append(encodings[0])
                all_names.append(user)
                print(f"  ✓ SUCCESS: {user} encoded successfully!\n")
            else:
                print(f"  ✗ ERROR: Could not generate encoding\n")
                
        except Exception as e:
            print(f"  ✗ ERROR: {e}\n")
            import traceback
            traceback.print_exc()
    
    # Save encodings
    if all_encodings:
        data = {"encodings": all_encodings, "names": all_names}
        
        with open("encodings.pickle", "wb") as f:
            pickle.dump(data, f)
        
        print(f"\n✓ Successfully saved {len(all_encodings)} encodings to encodings.pickle")
        print(f"Users encoded: {all_names}")
        return True
    else:
        print("\n✗ No faces could be encoded!")
        return False

if __name__ == "__main__":
    success = test_encoding()
    
    if success:
        print("\n✓ Encoding test PASSED")
        print("You can now use the login feature")
    else:
        print("\n✗ Encoding test FAILED")
        print("Please check the errors above and fix them")
        sys.exit(1)