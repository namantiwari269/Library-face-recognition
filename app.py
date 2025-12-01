from flask import Flask, render_template, Response, request, jsonify
import cv2
import face_recognition
import pickle
import os
import mysql.connector
import random
import string
import numpy as np
import traceback
import threading
import time

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Database config
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "password",
    "database": "smart_library"
}

def connect_db():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def generate_uid():
    prefix = "USR"
    block = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"{prefix}-{block}"

# Global state
class CameraState:
    def __init__(self):
        self.camera = None
        self.lock = threading.Lock()
        self.signup_mode = False
        self.login_mode = False
        self.signup_data = {}
    
    def get_camera(self):
        with self.lock:
            if self.camera is None or not self.camera.isOpened():
                self.camera = cv2.VideoCapture(0)
                self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                time.sleep(0.5)
            return self.camera
    
    def release_camera(self):
        with self.lock:
            if self.camera is not None:
                self.camera.release()
                self.camera = None

camera_state = CameraState()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/signup_page")
def signup_page():
    return render_template("signup.html")

@app.route("/login_page")
def login_page():
    try:
        encodings_file = "encodings.pickle"
        if not os.path.exists(encodings_file):
            return render_template("login.html", error="No registered users found. Please sign up first.")
        return render_template("login.html", error=None)
    except Exception as e:
        print(f"Error: {e}")
        return render_template("login.html", error=str(e))

@app.route("/start_signup", methods=["POST"])
def start_signup():
    try:
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        
        if not name:
            return jsonify({"success": False, "message": "Name is required!"})
        
        uid = generate_uid()
        camera_state.signup_data = {
            "name": name,
            "email": email,
            "uid": uid,
            "valid_frames": 0,
            "captured": False
        }
        camera_state.signup_mode = True
        
        return jsonify({"success": True, "uid": uid})
    except Exception as e:
        print(f"Error in start_signup: {e}")
        traceback.print_exc()
        return jsonify({"success": False, "message": str(e)})

def encode_face_immediate(uid):
    """Encode face immediately after capture"""
    try:
        print(f"Encoding face for {uid}...")
        encodings_file = "encodings.pickle"
        
        known_encodings = []
        known_names = []
        
        # Load existing encodings
        if os.path.exists(encodings_file):
            with open(encodings_file, "rb") as f:
                data = pickle.load(f)
                known_encodings = data["encodings"]
                known_names = data["names"]
            print(f"Loaded {len(known_encodings)} existing encodings")
        
        # Encode new face
        img_path = f"dataset/{uid}/{uid}.jpg"
        
        if not os.path.exists(img_path):
            print(f"ERROR: Image file not found: {img_path}")
            return False
        
        print(f"Loading image from: {img_path}")
        image = face_recognition.load_image_file(img_path)
        print(f"Image shape: {image.shape}")
        
        face_encodings = face_recognition.face_encodings(image)
        print(f"Found {len(face_encodings)} face(s) in image")
        
        if len(face_encodings) == 0:
            print("ERROR: No face detected in saved image!")
            return False
        
        encoding = face_encodings[0]
        
        # Check if user already exists
        if uid in known_names:
            idx = known_names.index(uid)
            known_encodings[idx] = encoding
            print(f"Updated encoding for {uid}")
        else:
            known_encodings.append(encoding)
            known_names.append(uid)
            print(f"Added new encoding for {uid}")
        
        # Save
        data = {"encodings": known_encodings, "names": known_names}
        with open(encodings_file, "wb") as f:
            pickle.dump(data, f)
        
        print(f"✓ Successfully encoded and saved face for {uid}")
        print(f"Total encodings: {len(known_encodings)}")
        return True
        
    except Exception as e:
        print(f"ERROR encoding face: {e}")
        traceback.print_exc()
        return False

def generate_signup_frames():
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_eye.xml")
    
    required_frames = 5
    
    try:
        cam = camera_state.get_camera()
        
        if not cam.isOpened():
            print("ERROR: Camera failed to open!")
            return
        
        print("Camera opened successfully for signup")
        
        while camera_state.signup_mode:
            success, frame = cam.read()
            if not success:
                print("Failed to read frame")
                time.sleep(0.1)
                continue
            
            if not camera_state.signup_data.get("captured", False):
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, 1.3, 5)
                
                if len(faces) == 1:
                    (x, y, w, h) = faces[0]
                    
                    if w < 120 or h < 120:
                        cv2.putText(frame, "Come closer!", (50, 50), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                        camera_state.signup_data["valid_frames"] = 0
                    else:
                        roi_gray = gray[y:y+h, x:x+w]
                        eyes = eye_cascade.detectMultiScale(roi_gray)
                        
                        if len(eyes) >= 2:
                            camera_state.signup_data["valid_frames"] += 1
                            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                            count = camera_state.signup_data['valid_frames']
                            cv2.putText(frame, f"Hold still... {count}/{required_frames}", 
                                       (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                            
                            if camera_state.signup_data["valid_frames"] >= required_frames:
                                uid = camera_state.signup_data["uid"]
                                user_folder = f"dataset/{uid}"
                                os.makedirs(user_folder, exist_ok=True)
                                
                                face_img = frame[y:y+h, x:x+w]
                                img_path = f"{user_folder}/{uid}.jpg"
                                cv2.imwrite(img_path, face_img)
                                print(f"✓ Face image saved: {img_path}")
                                
                                # Encode face immediately
                                if encode_face_immediate(uid):
                                    # Save to database
                                    try:
                                        db = connect_db()
                                        if db:
                                            cursor = db.cursor()
                                            sql = "INSERT INTO users (name, email, face_id) VALUES (%s, %s, %s)"
                                            cursor.execute(sql, (
                                                camera_state.signup_data["name"],
                                                camera_state.signup_data["email"],
                                                uid
                                            ))
                                            db.commit()
                                            db.close()
                                            print(f"✓ User saved to database")
                                            
                                            camera_state.signup_data["captured"] = True
                                            cv2.putText(frame, "SUCCESS! Registration Complete!", (30, 100), 
                                                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                                        else:
                                            print("ERROR: Database connection failed")
                                            cv2.putText(frame, "DB Error!", (50, 100), 
                                                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                                    except Exception as e:
                                        print(f"Database error: {e}")
                                        traceback.print_exc()
                                else:
                                    print("ERROR: Face encoding failed")
                                    cv2.putText(frame, "Encoding Failed! Try again", (50, 100), 
                                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                                    camera_state.signup_data["valid_frames"] = 0
                        else:
                            cv2.putText(frame, "Eyes not visible!", (50, 50), 
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                            camera_state.signup_data["valid_frames"] = 0
                else:
                    cv2.putText(frame, "Show only ONE face!", (50, 50), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    camera_state.signup_data["valid_frames"] = 0
            else:
                cv2.putText(frame, "Registration Complete!", (50, 50), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
            
            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                   
    except Exception as e:
        print(f"Error in generate_signup_frames: {e}")
        traceback.print_exc()

@app.route("/video_feed_signup")
def video_feed_signup():
    return Response(generate_signup_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/stop_signup")
def stop_signup():
    camera_state.signup_mode = False
    camera_state.release_camera()
    return jsonify({"success": True})

def generate_login_frames():
    try:
        encodings_file = "encodings.pickle"
        if not os.path.exists(encodings_file):
            print("No encodings file found")
            return
        
        with open(encodings_file, "rb") as f:
            data = pickle.load(f)
        
        known_encodings = data["encodings"]
        known_face_ids = data["names"]
        
        print(f"Loaded {len(known_encodings)} face encodings")
        
        cam = camera_state.get_camera()
        process_this_frame = True
        
        while camera_state.login_mode:
            success, frame = cam.read()
            if not success:
                print("Failed to read frame")
                time.sleep(0.1)
                continue
            
            if process_this_frame:
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                boxes = face_recognition.face_locations(rgb, model="hog")
                encodings = face_recognition.face_encodings(rgb, boxes)
                
                for (top, right, bottom, left), encoding in zip(boxes, encodings):
                    distances = face_recognition.face_distance(known_encodings, encoding)
                    
                    label = "UNKNOWN"
                    color = (0, 0, 255)
                    
                    if len(distances) > 0:
                        best_idx = np.argmin(distances)
                        best_dist = distances[best_idx]
                        
                        if best_dist < 0.60:
                            face_id = known_face_ids[best_idx]
                            
                            try:
                                db = connect_db()
                                if db:
                                    cursor = db.cursor()
                                    cursor.execute("SELECT user_id, name FROM users WHERE face_id = %s", (face_id,))
                                    res = cursor.fetchone()
                                    db.close()
                                    
                                    if res:
                                        user_id, name = res
                                        label = f"{name} | {face_id}"
                                        color = (0, 255, 0)
                                    else:
                                        label = f"{face_id}"
                                        color = (255, 165, 0)
                            except Exception as e:
                                print(f"Database error: {e}")
                                label = f"{face_id}"
                                color = (255, 165, 0)
                    
                    cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                    cv2.putText(frame, label, (left, top - 10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            process_this_frame = not process_this_frame
            
            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                   
    except Exception as e:
        print(f"Error in generate_login_frames: {e}")
        traceback.print_exc()

@app.route("/start_login")
def start_login():
    try:
        if not os.path.exists("encodings.pickle"):
            return jsonify({"success": False, "message": "No registered users. Please sign up first."})
        
        camera_state.login_mode = True
        return jsonify({"success": True})
    except Exception as e:
        print(f"Error in start_login: {e}")
        traceback.print_exc()
        return jsonify({"success": False, "message": str(e)})

@app.route("/video_feed_login")
def video_feed_login():
    return Response(generate_login_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/stop_login")
def stop_login():
    camera_state.login_mode = False
    camera_state.release_camera()
    return jsonify({"success": True})

if __name__ == "__main__":
    os.makedirs("dataset", exist_ok=True)
    os.makedirs("templates", exist_ok=True)
    
    print("\n" + "="*50)
    print("Face Recognition System Starting...")
    print("="*50)
    print("Make sure you have:")
    print("1. MySQL database 'smart_library' created")
    print("2. Table 'users' with columns: user_id, name, email, face_id")
    print("3. Camera connected and working")
    print("="*50 + "\n")
    
    app.run(debug=True, threaded=True, host='0.0.0.0', port=5000)