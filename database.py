import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "campus.db"


def get_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db():
    with get_connection() as con:
        con.executescript("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT NOT NULL,
            register_number TEXT NOT NULL,
            department TEXT NOT NULL,
            attendance_date TEXT NOT NULL,
            status TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT NOT NULL,
            register_number TEXT NOT NULL,
            category TEXT NOT NULL,
            complaint TEXT NOT NULL,
            complaint_date TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Pending'
        );

        CREATE TABLE IF NOT EXISTS leaves (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT NOT NULL,
            register_number TEXT NOT NULL,
            department TEXT NOT NULL,
            leave_date TEXT NOT NULL,
            reason TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Pending'
        );

        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            register_number TEXT UNIQUE,
            name TEXT NOT NULL,
            department TEXT NOT NULL,
            year TEXT NOT NULL,
            email TEXT DEFAULT ''
        );

        CREATE TABLE IF NOT EXISTS quiz_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT NOT NULL,
            register_number TEXT NOT NULL,
            score INTEGER NOT NULL,
            total INTEGER NOT NULL,
            quiz_date TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS maintenance_tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reporter_name TEXT NOT NULL,
            location TEXT NOT NULL,
            equipment TEXT NOT NULL,
            description TEXT NOT NULL,
            reported_date TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Pending'
        );

        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT NOT NULL,
            course TEXT NOT NULL,
            rating INTEGER NOT NULL,
            comments TEXT NOT NULL,
            submitted_date TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS learning_materials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            subject TEXT NOT NULL,
            material_type TEXT NOT NULL,
            url TEXT NOT NULL,
            description TEXT NOT NULL
        );
        """)

        # Seed only when these tables are empty; existing user data is not overwritten.
        if con.execute("SELECT COUNT(*) FROM students").fetchone()[0] == 0:
            con.executemany(
                """INSERT INTO students
                   (register_number, name, department, year, email)
                   VALUES (?, ?, ?, ?, ?)""",
                [
                    ("24CSE001", "Arun Kumar", "CSE", "III", "arun@example.com"),
                    ("24ECE002", "Priya S", "ECE", "III", "priya@example.com"),
                    ("24CSE003", "Kavin R", "CSE", "III", "kavin@example.com"),
                ],
            )

        if con.execute("SELECT COUNT(*) FROM learning_materials").fetchone()[0] == 0:
            con.executemany(
                """INSERT INTO learning_materials
                   (title, subject, material_type, url, description)
                   VALUES (?, ?, ?, ?, ?)""",
                [
                    ("Python Programming Basics", "Python", "Documentation",
                     "https://docs.python.org/3/tutorial/", "Official Python tutorial for beginners."),
                    ("HTML Learning Guide", "Web Development", "Tutorial",
                     "https://developer.mozilla.org/en-US/docs/Learn/HTML", "Learn the structure of web pages."),
                    ("SQLite Documentation", "Database", "Documentation",
                     "https://www.sqlite.org/docs.html", "Reference for SQLite database features."),
                    ("Flask Quickstart", "Python Web", "Documentation",
                     "https://flask.palletsprojects.com/en/stable/quickstart/", "Build a web app using Flask."),
                ],
            )


def fetch_all(query, params=()):
    with get_connection() as con:
        return con.execute(query, params).fetchall()


def fetch_one(query, params=()):
    with get_connection() as con:
        return con.execute(query, params).fetchone()


def execute(query, params=()):
    with get_connection() as con:
        cursor = con.execute(query, params)
        return cursor.lastrowid


def add_attendance(name, reg_no, department, attendance_date, status="Present"):
    return execute(
        """INSERT INTO attendance
           (student_name, register_number, department, attendance_date, status)
           VALUES (?, ?, ?, ?, ?)""",
        (name, reg_no, department, attendance_date, status),
    )


def get_attendance():
    return fetch_all("SELECT * FROM attendance ORDER BY attendance_date DESC, id DESC")


def add_complaint(name, reg_no, category, complaint, complaint_date, status="Pending"):
    return execute(
        """INSERT INTO complaints
           (student_name, register_number, category, complaint, complaint_date, status)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (name, reg_no, category, complaint, complaint_date, status),
    )


def get_complaints():
    return fetch_all("SELECT * FROM complaints ORDER BY id DESC")


def add_leave(name, reg_no, department, leave_date, reason, status="Pending"):
    return execute(
        """INSERT INTO leaves
           (student_name, register_number, department, leave_date, reason, status)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (name, reg_no, department, leave_date, reason, status),
    )


def get_leaves():
    return fetch_all("SELECT * FROM leaves ORDER BY id DESC")


def update_leave_status(leave_id, status):
    execute("UPDATE leaves SET status=? WHERE id=?", (status, leave_id))


def get_dashboard_stats():
    return {
        "students": fetch_one("SELECT COUNT(*) AS n FROM students")["n"],
        "attendance": fetch_one("SELECT COUNT(*) AS n FROM attendance")["n"],
        "pending_complaints": fetch_one(
            "SELECT COUNT(*) AS n FROM complaints WHERE status='Pending'")["n"],
        "pending_leaves": fetch_one(
            "SELECT COUNT(*) AS n FROM leaves WHERE status='Pending'")["n"],
        "open_tickets": fetch_one(
            "SELECT COUNT(*) AS n FROM maintenance_tickets WHERE status != 'Resolved'")["n"],
        "quiz_attempts": fetch_one("SELECT COUNT(*) AS n FROM quiz_results")["n"],
    }
