#!/usr/bin/env python3
"""
Add sample books to your library database
"""

import mysql.connector

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "password",  # Change this
    "database": "smart_library"
}

# Sample books data
BOOKS = [
    ("B001", "To Kill a Mockingbird", "Harper Lee", "Fiction"),
    ("B002", "1984", "George Orwell", "Science Fiction"),
    ("B003", "Pride and Prejudice", "Jane Austen", "Romance"),
    ("B004", "The Great Gatsby", "F. Scott Fitzgerald", "Fiction"),
    ("B005", "Harry Potter and the Sorcerer's Stone", "J.K. Rowling", "Fantasy"),
    ("B006", "The Hobbit", "J.R.R. Tolkien", "Fantasy"),
    ("B007", "The Catcher in the Rye", "J.D. Salinger", "Fiction"),
    ("B008", "The Lord of the Rings", "J.R.R. Tolkien", "Fantasy"),
    ("B009", "Animal Farm", "George Orwell", "Political Fiction"),
    ("B010", "Brave New World", "Aldous Huxley", "Science Fiction"),
    ("B011", "The Chronicles of Narnia", "C.S. Lewis", "Fantasy"),
    ("B012", "Fahrenheit 451", "Ray Bradbury", "Science Fiction"),
    ("B013", "Jane Eyre", "Charlotte Brontë", "Romance"),
    ("B014", "Wuthering Heights", "Emily Brontë", "Romance"),
    ("B015", "The Picture of Dorian Gray", "Oscar Wilde", "Gothic Fiction"),
    ("B016", "Moby-Dick", "Herman Melville", "Adventure"),
    ("B017", "The Odyssey", "Homer", "Epic Poetry"),
    ("B018", "Crime and Punishment", "Fyodor Dostoevsky", "Psychological Fiction"),
    ("B019", "The Divine Comedy", "Dante Alighieri", "Epic Poetry"),
    ("B020", "Alice's Adventures in Wonderland", "Lewis Carroll", "Fantasy"),
]

def add_books():
    print("\n" + "="*60)
    print("Adding Sample Books to Library")
    print("="*60)
    
    try:
        # Connect to database
        print("\n[1/3] Connecting to database...")
        db = mysql.connector.connect(**DB_CONFIG)
        cursor = db.cursor()
        print("✓ Connected")
        
        # Check if books table exists
        print("\n[2/3] Checking books table...")
        cursor.execute("SHOW TABLES LIKE 'books'")
        if not cursor.fetchone():
            print("✗ Books table not found!")
            print("Please run your SQL setup script first.")
            return False
        print("✓ Books table exists")
        
        # Insert books
        print("\n[3/3] Adding books...")
        added = 0
        skipped = 0
        
        for book_id, title, author, genre in BOOKS:
            try:
                cursor.execute("""
                    INSERT INTO books (book_id, title, author, genre)
                    VALUES (%s, %s, %s, %s)
                """, (book_id, title, author, genre))
                print(f"  ✓ Added: {title} by {author}")
                added += 1
            except mysql.connector.IntegrityError:
                print(f"  ⊘ Skipped (already exists): {title}")
                skipped += 1
        
        db.commit()
        
        # Show summary
        cursor.execute("SELECT COUNT(*) FROM books")
        total = cursor.fetchone()[0]
        
        print("\n" + "="*60)
        print("✓ Books Added Successfully!")
        print("="*60)
        print(f"Added: {added} books")
        print(f"Skipped: {skipped} books (already existed)")
        print(f"Total books in library: {total}")
        print("="*60 + "\n")
        
        cursor.close()
        db.close()
        
        return True
        
    except mysql.connector.Error as err:
        print(f"\n✗ Database Error: {err}")
        return False
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import sys
    success = add_books()
    sys.exit(0 if success else 1)