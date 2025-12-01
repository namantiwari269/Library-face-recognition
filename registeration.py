import mysql.connector
import subprocess
import random
import string
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ---------- DATABASE CONFIG ----------
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "password",  # change this
    "database": "smart_library"
}

def connect_db():
    return mysql.connector.connect(**DB_CONFIG)


# ---------- UID GENERATOR ----------
def generate_uid():
    prefix = "USR"
    block = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"{prefix}-{block}"


# ---------- ADD USER TO DATABASE ----------
def add_user(name, email, uid):
    db = connect_db()
    cursor = db.cursor()

    sql = "INSERT INTO users (name, email, face_id) VALUES (%s, %s, %s)"
    cursor.execute(sql, (name, email, uid))
    db.commit()

    return cursor.lastrowid


# ---------- MAIN FLOW ----------
if __name__ == "__main__":
    print("\n=== REGISTER NEW USER ===")

    name = input("Enter Full Name: ").strip()
    email = input("Enter Email (optional): ").strip()

    if not name:
        print("❌ Name is required!")
        sys.exit(1)

    uid = generate_uid()
    print(f"Generated Unique Face ID: {uid}")

    print("\n📸 Starting face capture...")
    
    # run save_face.py with UID
    python_exec = sys.executable
    proc = subprocess.run(
        [python_exec, "save_faces.py", uid],
        cwd=BASE_DIR
    )

    if proc.returncode != 0:
        print("❌ Registration cancelled during face capture.")
        sys.exit(1)

    # Now add to DB
    user_id = add_user(name, email, uid)

    print("\n🎉 Registration Complete!")
    print(f"Name: {name}")
    print(f"Face ID: {uid}")
    print(f"Database User ID: {user_id}")
