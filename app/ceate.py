import sqlite3

# Create a new SQLite database (or connect to it if it already exists)
conn = sqlite3.connect('iaasdb.sqlite')
cursor = conn.cursor()

# SQL statements to create tables
create_tables_sql = """
CREATE TABLE admins (
    admin_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE exams (
    exam_id INTEGER PRIMARY KEY AUTOINCREMENT,
    lecturer_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    exam_key TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN NOT NULL CHECK (is_active IN (0, 1))
);

CREATE TABLE exam_results (
    result_id INTEGER PRIMARY KEY AUTOINCREMENT,
    exam_id INTEGER NOT NULL,
    lecturer_id INTEGER NOT NULL,
    normal_distribution TEXT
);

CREATE TABLE lectures (
    lecturer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE questions (
    question_id INTEGER PRIMARY KEY AUTOINCREMENT,
    exam_id INTEGER NOT NULL,
    text TEXT NOT NULL,
    correct_answer TEXT NOT NULL,
    question_type TEXT NOT NULL,
    options TEXT
);

CREATE TABLE responses (
    response_id INTEGER PRIMARY KEY AUTOINCREMENT,
    enrollment_id INTEGER NOT NULL,
    question_id INTEGER NOT NULL,
    student_answer TEXT NOT NULL,
    is_correct BOOLEAN NOT NULL CHECK (is_correct IN (0, 1)),
    score INTEGER NOT NULL
);

CREATE TABLE students (
    student_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    registration_date DATE NOT NULL
    password TEXT NOT NULL
);

);

CREATE TABLE student_exam_enrollments (
    enrollment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    exam_id INTEGER NOT NULL,
    started_at DATETIME NOT NULL,
    completed_at DATETIME,
    score INTEGER
);
"""

# Execute the SQL statements to create the tables
cursor.executescript(create_tables_sql)

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Database and tables created successfully.")
