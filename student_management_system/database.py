import sqlite3
from werkzeug.security import generate_password_hash

DB_PATH = "students.db"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            roll_no TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            course TEXT NOT NULL,
            year INTEGER NOT NULL,
            gpa REAL,
            status TEXT NOT NULL DEFAULT 'Active',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
    """)
    if not conn.execute("SELECT 1 FROM users").fetchone():
        conn.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)",
                     ("admin", generate_password_hash("admin123")))
    if not conn.execute("SELECT 1 FROM students").fetchone():
        demo = [
            ("CS101", "Aarav Sharma", "aarav@example.com", "9876500001", "Computer Science", 2, 8.7, "Active"),
            ("CS102", "Diya Patil", "diya@example.com", "9876500002", "Computer Science", 3, 9.1, "Active"),
            ("ME201", "Rohan Deshmukh", "rohan@example.com", "9876500003", "Mechanical", 1, 7.4, "Active"),
            ("EC301", "Isha Kulkarni", "isha@example.com", "9876500004", "Electronics", 4, 8.2, "Graduated"),
            ("BA401", "Kabir Joshi", "kabir@example.com", "9876500005", "Business Admin", 2, 6.9, "Inactive"),
        ]
        conn.executemany("""INSERT INTO students
            (roll_no, name, email, phone, course, year, gpa, status)
            VALUES (?,?,?,?,?,?,?,?)""", demo)
    conn.commit()
    conn.close()
