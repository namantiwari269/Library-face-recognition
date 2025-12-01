# Setup Guide for Your Existing SQL Schema

## Your Database Schema Works! ✅

Your existing schema is compatible. Here's how to set it up:

## Step 1: Run Your SQL Script

Since you already have your SQL, just run it in MySQL:

```bash
mysql -u root -p < your_sql_file.sql
```

Or manually in MySQL:

```sql
CREATE DATABASE smart_library;
USE smart_library;

CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    face_id VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE books (
    book_id VARCHAR(100) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(255),
    genre VARCHAR(50)
);

CREATE TABLE borrow_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    book_id VARCHAR(100) NOT NULL,
    borrow_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    return_time DATETIME,
    status ENUM('BORROWED','RETURNED') DEFAULT 'BORROWED',
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (book_id) REFERENCES books(book_id)
);
```

## Step 2: Add Sample Books

Run the Python script to add 20 sample books:

```bash
python add_sample_books.py
```

This adds books with IDs like B001, B002, etc.

## Step 3: Update Database Password

Edit the `app.py` file (line 16) and `add_sample_books.py` (line 9):

```python
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "YOUR_PASSWORD_HERE",  # <-- Change this
    "database": "smart_library"
}
```

## Step 4: Create Templates Folder

Make sure these HTML files are in a `templates/` folder:
- `index.html`
- `signup.html`
- `login.html`
- `dashboard_simple.html`
- `books_simple.html`

## Step 5: Run the Application

```bash
python app.py
```

Visit: http://localhost:5000

## Key Differences from Standard Schema

Your schema uses:
- `book_id` as **VARCHAR(100)** instead of auto-increment INT
- Table named `borrow_history` instead of `borrowings`
- Status field as **ENUM('BORROWED','RETURNED')**
- Column `id` for borrow_history primary key instead of `borrow_id`

The adapted `app.py` handles all these differences automatically! 🎉

## Testing the System

1. **Sign Up**: Register your face
2. **Login**: Get recognized and see "Welcome, [Your Name]!"
3. **Browse**: View all 20 available books
4. **Borrow**: Click "Borrow This Book"
5. **Return**: Go to dashboard and click "Return Book"

## Verifying Data

Check your database:

```sql
-- See all users
SELECT * FROM users;

-- See all books
SELECT * FROM books;

-- See borrowing history
SELECT * FROM borrow_history;

-- See currently borrowed books
SELECT b.title, u.name, bh.borrow_time
FROM borrow_history bh
JOIN books b ON bh.book_id = b.book_id
JOIN users u ON bh.user_id = u.user_id
WHERE bh.status = 'BORROWED';
```

## Troubleshooting

### If books don't show up:
```bash
python add_sample_books.py
```

### If login doesn't work:
```bash
# Check if face was encoded
python -c "import pickle; data=pickle.load(open('encodings.pickle','rb')); print(data['names'])"
```

### Check database connection:
```bash
python -c "
import mysql.connector
db = mysql.connector.connect(host='localhost', user='root', password='YOUR_PASSWORD', database='smart_library')
print('✓ Connected')
"
```

## File Structure

```
your-project/
├── app.py                      # Main Flask app (use adapted version)
├── add_sample_books.py         # Add books to database
├── dataset/                    # Face images (auto-created)
├── templates/                  # HTML files
│   ├── index.html
│   ├── signup.html
│   ├── login.html
│   ├── dashboard_simple.html
│   └── books_simple.html
└── encodings.pickle            # Face encodings (auto-created)
```

## Your Schema is Perfect For:

✅ Simple book IDs (B001, B002, etc.)
✅ Clear status tracking (BORROWED/RETURNED)
✅ Complete borrow history
✅ Flexible book_id format (can use ISBN, custom codes, etc.)

You're all set! Your existing schema works perfectly with the face recognition system! 🚀