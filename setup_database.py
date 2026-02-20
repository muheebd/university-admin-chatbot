import sqlite3
from werkzeug.security import generate_password_hash
import random

def create_mock_database():
    # Connect to SQLite (creates university.db in your folder)
    conn = sqlite3.connect('university.db')
    cursor = conn.cursor()

    # Drop tables if they exist so we can run this cleanly multiple times
    tables = ['students', 'payments_history', 'course_registration', 'accommodation', 'results']
    for table in tables:
        cursor.execute(f'DROP TABLE IF EXISTS {table}')

    # 1. Create Students Table
    cursor.execute('''
        CREATE TABLE students (
            matric_no TEXT PRIMARY KEY,
            pin_hash TEXT,
            full_name TEXT,
            faculty TEXT,
            department TEXT,
            programme TEXT,
            level INTEGER,
            active_session TEXT,
            enrolment_status TEXT
        )
    ''')

    # 2. Create Payments History Table
    cursor.execute('''
        CREATE TABLE payments_history (
            tx_id TEXT PRIMARY KEY,
            matric_no TEXT,
            payment_type TEXT,
            amount REAL,
            date TEXT,
            receipt_no TEXT,
            status TEXT,
            FOREIGN KEY(matric_no) REFERENCES students(matric_no)
        )
    ''')

    # 3. Create Course Registration Table
    cursor.execute('''
        CREATE TABLE course_registration (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            matric_no TEXT,
            course_code TEXT,
            course_title TEXT,
            units INTEGER,
            semester TEXT,
            session TEXT,
            extra_unit_status TEXT,
            FOREIGN KEY(matric_no) REFERENCES students(matric_no)
        )
    ''')

    # 4. Create Accommodation Table
    cursor.execute('''
        CREATE TABLE accommodation (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            matric_no TEXT,
            hostel_name TEXT,
            room_number TEXT,
            status TEXT,
            FOREIGN KEY(matric_no) REFERENCES students(matric_no)
        )
    ''')

    # 5. Create Results Table
    cursor.execute('''
        CREATE TABLE results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            matric_no TEXT,
            session TEXT,
            semester TEXT,
            gpa REAL,
            cgpa REAL,
            FOREIGN KEY(matric_no) REFERENCES students(matric_no)
        )
    ''')

    # =========================================================
    # 🎓 INJECTING YOUR EXACT AL-HIKMAH PROFILE
    # =========================================================
    
    # We hash the PIN '1234' for Cyber Security best practices
    pin_hash = generate_password_hash("1234")
    my_matric = "22/03CYB059"

    # Insert Your Student Demographics
    cursor.execute('''
        INSERT INTO students VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (my_matric, pin_hash, 'Lawal, Muheebdeen Ayodeji', 'Computing, Engineering And Technology', 
          'Computer Science', 'Cyber Security', 400, '2025/2026', 'Failed: Outstanding Payment'))

    # Insert Your Payments (Showing an outstanding balance setup)
    cursor.execute('''
        INSERT INTO payments_history VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', ('TXN-2025-9981', my_matric, 'Sundry Fee', 150000.00, '2025-11-15', 'RCPT-1102A', 'Successful'))
    
    cursor.execute('''
        INSERT INTO payments_history VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', ('TXN-2025-9982', my_matric, 'Tuition Fee (Part)', 400000.00, '2025-12-01', 'RCPT-1102B', 'Successful'))
    # (The portal noted an outstanding payment, which the bot will calculate later!)

    # Insert Your Academics (Courses)
    courses = [
        ('CYB401', 'Cryptography and Network Security', 3, '1st Semester', '2025/2026', 'None'),
        ('CYB403', 'Cyber Threat Intelligence', 2, '1st Semester', '2025/2026', 'None'),
        ('CYB405', 'Digital Forensics (Extra Unit)', 3, '1st Semester', '2025/2026', 'Approved')
    ]
    for course in courses:
        cursor.execute('''
            INSERT INTO course_registration (matric_no, course_code, course_title, units, semester, session, extra_unit_status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (my_matric, course[0], course[1], course[2], course[3], course[4], course[5]))

    # Insert Your Accommodation
    cursor.execute('''
        INSERT INTO accommodation (matric_no, hostel_name, room_number, status)
        VALUES (?, ?, ?, ?)
    ''', (my_matric, 'Male Hostel A', 'Room 42B', 'Allocated'))

    # Insert Your Results (Showcasing your 4.32 CGPA)
    cursor.execute('''
        INSERT INTO results (matric_no, session, semester, gpa, cgpa)
        VALUES (?, ?, ?, ?, ?)
    ''', (my_matric, '2024/2025', '2nd Semester', 4.50, 4.32))

    # =========================================================
    # Commit changes and close
    # =========================================================
    conn.commit()
    conn.close()
    
    print("\n✅ SUCCESS: 'university.db' has been created!")
    print("🎓 5 Relational Tables Generated: Students, Payments, Courses, Accommodation, Results.")
    print(f"🔐 Master Test Profile Loaded: {my_matric} | PIN: 1234\n")

if __name__ == "__main__":
    create_mock_database()