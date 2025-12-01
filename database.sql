use sys;

select * from sys_config;
CREATE DATABASE smart_library;
USE smart_library;

-- USERS TABLE
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    face_id VARCHAR(255) NOT NULL UNIQUE
);

-- BOOKS TABLE
CREATE TABLE books (
    book_id VARCHAR(100) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(255),
    genre VARCHAR(50)
);

-- BORROW HISTORY TABLE
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
