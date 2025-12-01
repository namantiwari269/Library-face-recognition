import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="password",
    database="smart_library"
)

cursor = db.cursor()
cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
cursor.execute("TRUNCATE TABLE users;")
cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")

db.commit()

print("All users deleted.")
