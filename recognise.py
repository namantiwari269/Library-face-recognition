import face_recognition
import cv2
import numpy as np
import pickle
import mysql.connector

# ---------- SQL SETUP ----------
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="password",   # CHANGE THIS
    database="smart_library"
)

cursor = db.cursor()

def get_user_details(face_id):
    cursor.execute("SELECT user_id, name FROM users WHERE face_id = %s", (face_id,))
    res = cursor.fetchone()
    if res:
        return res  # (user_id, name)
    return None


# ---------- LOAD ENCODINGS ----------
print("Loading encodings...")
data = pickle.load(open("encodings.pickle", "rb"))

known_encodings = data["encodings"]
known_face_ids = data["names"]    # These are your USR-XXXXX IDs


# ---------- START CAMERA ----------
cap = cv2.VideoCapture(0)

process_this_frame = True

while True:
    ret, frame = cap.read()
    if not ret:
        break

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    if process_this_frame:

        boxes = face_recognition.face_locations(rgb, model="hog")
        encodings = face_recognition.face_encodings(rgb, boxes)

        labels = []  # what we will show (user_name + face_id)

        for encoding in encodings:
            distances = face_recognition.face_distance(known_encodings, encoding)

            face_id = "UNKNOWN"
            label = "UNKNOWN"

            if len(distances) > 0:
                best_idx = np.argmin(distances)
                best_dist = distances[best_idx]

                if best_dist < 0.60:    # threshold for recognition
                    face_id = known_face_ids[best_idx]

                    # Lookup user from SQL
                    details = get_user_details(face_id)

                    if details:
                        user_id, name = details
                        label = f"{name} | {face_id} | ID:{user_id}"
                    else:
                        label = face_id   # fallback if DB missing data

            labels.append(label)

    process_this_frame = not process_this_frame

    # ---------- DRAW ----------
    for ((top, right, bottom, left), label) in zip(boxes, labels):
        cv2.rectangle(frame, (left, top), (right, bottom), (0,255,0), 2)
        cv2.putText(frame, label, (left, top - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)

    cv2.imshow("Face Recognition", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


cap.release()
cv2.destroyAllWindows()
