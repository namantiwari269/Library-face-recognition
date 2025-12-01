import cv2
import os
import subprocess
import sys

if len(sys.argv) > 1:
    username = sys.argv[1]      # get username passed from register_user.py
else:
    username = input("Enter username: ").strip()

user_folder = f"dataset/{username}"
os.makedirs(user_folder, exist_ok=True)

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_eye.xml")

cap = cv2.VideoCapture(0)

valid_frames = 0
required_frames = 5  # must show face properly for 5 frames

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    if len(faces) == 1:
        (x, y, w, h) = faces[0]

        # Only accept bigger/close faces
        if w < 120 or h < 120:
            cv2.putText(frame, "Come closer to the camera!",
                        (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,255), 2)
            valid_frames = 0
        else:
            roi_gray = gray[y:y+h, x:x+w]
            eyes = eye_cascade.detectMultiScale(roi_gray)

            if len(eyes) >= 2:  # both eyes visible
                valid_frames += 1
                cv2.rectangle(frame, (x,y),(x+w,y+h),(0,255,0),2)
                cv2.putText(frame, "Hold still...", (50, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
            else:
                cv2.putText(frame, "Eyes not visible!",
                            (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,255), 2)
                valid_frames = 0
    else:
        cv2.putText(frame, "Show only ONE face!",
                    (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7,(0,0,255),2)
        valid_frames = 0

    if valid_frames >= required_frames:
        face_img = frame[y:y+h, x:x+w]
        cv2.imwrite(f"{user_folder}/{username}.jpg", face_img)
        print("✓ Face correctly captured!")
        print("➡️ Encoding face, please wait...")
        subprocess.run(
    [
        "/opt/miniconda3/bin/python3",  # <-- your working Python
        "encode_faces.py"
    ]
)

        print("✓ Face encoded successfully!")
        break

    cv2.imshow("Face Capture (show eyes!)", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        print("✕ Cancelled")
        break

cap.release()
cv2.destroyAllWindows()
