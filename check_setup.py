#!/usr/bin/env python3
"""
Setup Checker for Face Recognition System
Run this to diagnose issues
"""

import os
import sys

def check_directories():
    print("\n=== Checking Directories ===")
    required_dirs = ['dataset', 'templates']
    for d in required_dirs:
        if os.path.exists(d):
            print(f"✓ {d}/ exists")
        else:
            print(f"✗ {d}/ missing - creating...")
            os.makedirs(d, exist_ok=True)

def check_files():
    print("\n=== Checking Files ===")
    required_files = [
        ('templates/index.html', 'HTML template'),
        ('templates/signup.html', 'Signup page'),
        ('templates/login.html', 'Login page'),
        ('app.py', 'Main Flask app')
    ]
    
    for filepath, desc in required_files:
        if os.path.exists(filepath):
            print(f"✓ {filepath} exists ({desc})")
        else:
            print(f"✗ {filepath} missing ({desc})")

def check_encodings():
    print("\n=== Checking Encodings ===")
    if os.path.exists('encodings.pickle'):
        import pickle
        try:
            with open('encodings.pickle', 'rb') as f:
                data = pickle.load(f)
            print(f"✓ encodings.pickle exists")
            print(f"  - {len(data['encodings'])} users encoded")
            print(f"  - User IDs: {', '.join(data['names'])}")
        except Exception as e:
            print(f"✗ encodings.pickle corrupt: {e}")
    else:
        print("ℹ encodings.pickle doesn't exist (no users registered yet)")

def check_database():
    print("\n=== Checking Database ===")
    try:
        import mysql.connector
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="password",
            database="smart_library"
        )
        cursor = db.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        print(f"✓ Database connected")
        print(f"  - {count} users in database")
        
        cursor.execute("SELECT user_id, name, face_id FROM users LIMIT 5")
        users = cursor.fetchall()
        if users:
            print("  - Sample users:")
            for uid, name, fid in users:
                print(f"    • {name} ({fid})")
        db.close()
    except Exception as e:
        print(f"✗ Database error: {e}")

def check_modules():
    print("\n=== Checking Python Modules ===")
    modules = [
        'flask',
        'cv2',
        'face_recognition',
        'mysql.connector',
        'numpy',
        'pickle'
    ]
    
    for module in modules:
        try:
            if module == 'mysql.connector':
                __import__('mysql.connector')
            else:
                __import__(module)
            print(f"✓ {module} installed")
        except ImportError:
            print(f"✗ {module} not installed")
            if module == 'cv2':
                print(f"  Install with: pip install opencv-python")
            elif module == 'mysql.connector':
                print(f"  Install with: pip install mysql-connector-python")
            else:
                print(f"  Install with: pip install {module}")

def check_camera():
    print("\n=== Checking Camera ===")
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                print("✓ Camera is working")
                print(f"  - Resolution: {frame.shape[1]}x{frame.shape[0]}")
            else:
                print("✗ Camera found but can't read frames")
            cap.release()
        else:
            print("✗ Camera not accessible")
    except Exception as e:
        print(f"✗ Camera error: {e}")

def main():
    print("=" * 50)
    print("Face Recognition System - Setup Checker")
    print("=" * 50)
    
    check_modules()
    check_directories()
    check_files()
    check_database()
    check_encodings()
    check_camera()
    
    print("\n" + "=" * 50)
    print("Diagnosis Complete!")
    print("=" * 50)
    print("\nIf you see any ✗ marks, fix those issues first.")
    print("Then run: python app.py")

if __name__ == "__main__":
    main()