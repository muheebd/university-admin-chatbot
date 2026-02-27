import sqlite3
from werkzeug.security import generate_password_hash
import random

def create_mock_database():
    # Connect to SQLite (creates university.db in your folder)
    conn = sqlite3.connect('university.db')
    cursor = conn.cursor()

    # Drop tables if they exist so we can run this cleanly multiple times
    tables = ['students', 'finances', 'payments_history', 'course_registration', 'accommodation', 'results']
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

    # 2. Create Finances Table (tracks total billing, payments, and clearance)
    cursor.execute('''
        CREATE TABLE finances (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            matric_no TEXT UNIQUE,
            total_billed REAL,
            amount_paid REAL,
            balance REAL,
            clearance_status TEXT,
            FOREIGN KEY(matric_no) REFERENCES students(matric_no)
        )
    ''')

    # 3. Create Payments History Table
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
    # 🎓 INJECTING YOUR EXACT AL-HIKMAH MASTER PROFILE
    # =========================================================
    
    # We hash the PIN '1234' for Cyber Security best practices
    pin_hash = generate_password_hash("1234")
    my_matric = "22/03CYB059"

    # Insert Your Student Demographics
    cursor.execute('''
        INSERT INTO students VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (my_matric, pin_hash, 'Lawal, Muheebdeen Ayodeji', 'Faculty of Computing, Engineering and Technology', 
          'Computer Science', 'B.Sc. (Hons) Cyber Security', 400, '2025/2026', 'Failed: Outstanding Payment'))

    # Insert Your Payments
    cursor.execute('''
        INSERT INTO payments_history VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', ('TXN-2025-9981', my_matric, 'Sundry Fee', 150000.00, '2025-11-15', 'RCPT-1102A', 'Successful'))

    # Insert Your Finances Record
    cursor.execute('''
        INSERT INTO finances (matric_no, total_billed, amount_paid, balance, clearance_status)
        VALUES (?, ?, ?, ?, ?)
    ''', (my_matric, 850000.00, 150000.00, 700000.00, 'Not Cleared - Outstanding Balance'))
    
    # Insert Your Academics (Courses)
    cursor.execute('''
        INSERT INTO course_registration (matric_no, course_code, course_title, units, semester, session, extra_unit_status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (my_matric, 'CYB405', 'Digital Forensics (Extra Unit)', 3, '1st Semester', '2025/2026', 'Approved'))

    # Insert Your Accommodation
    cursor.execute('''
        INSERT INTO accommodation (matric_no, hostel_name, room_number, status)
        VALUES (?, ?, ?, ?)
    ''', (my_matric, 'Male Hostel A', 'Room 42B', 'Allocated'))

    # Insert Your Results
    cursor.execute('''
        INSERT INTO results (matric_no, session, semester, gpa, cgpa)
        VALUES (?, ?, ?, ?, ?)
    ''', (my_matric, '2024/2025', '2nd Semester', 4.50, 4.32))

    # =========================================================
    # 🌍 GENERATING UNIVERSITY-WIDE STUDENTS (REAL DATA)
    # =========================================================
    
    # Mapped directly from the Al-Hikmah Website provided
    faculties_data = {
        'Faculty of Humanities and Social Sciences': [
            ('History and International Studies', 'B.A (Hons) History and International Relations', 'HIR'),
            ('Islamic Studies', 'B.A (Hons) Islamic Studies', 'ISS'),
            ('Languages', 'B.A (Hons) English', 'ENG'),
            ('Languages', 'B.A (Hons) Arabic', 'ARA'),
            ('Mass Communication', 'B.Sc. (Hons) Mass Communication', 'MAC'),
            ('Political and Public Administration', 'B.Sc. (Hons) Political Science', 'POL'),
            ('Sociology', 'B.Sc. (Hons) Sociology', 'SOC')
        ],
        'Faculty of Management Sciences': [
            ('Accounting', 'B.Sc. (Hons) Accounting', 'ACC'),
            ('Banking and Finance', 'B.Sc. (Hons) Banking and Finance', 'BNK'),
            ('Business Administration', 'B.Sc. (Hons) Business Administration', 'BUS'),
            ('Economics', 'B.Sc. (Hons) Economics', 'ECO')
        ],
        'Faculty of Education': [
            ('Education Management', 'B.Ed. Educational Management', 'EDM'),
            ('Science Education', 'B.Sc. (Ed.) Computer Science', 'EDS'),
            ('Arts and Social Science Education', 'B.A. (Ed.) English', 'EDA'),
            ('Library and Information Science', 'BLIS Library and Information Science', 'LIS')
        ],
        'Faculty of Natural and Applied Sciences': [
            ('Biological Sciences', 'B.Sc. (Hons) Microbiology', 'MCB'),
            ('Biological Sciences', 'B.Sc. (Hons) Biochemistry', 'BCH'),
            ('Chemical and Geological Sciences', 'B.Sc. (Hons) Industrial Chemistry', 'ICH'),
            ('Chemical and Geological Sciences', 'B.Sc. (Hons) Geology', 'GLY'),
            ('Physical Sciences', 'B.Sc. (Hons) Physics with Electronics', 'PWE'),
            ('Physical Sciences', 'B.Sc. (Hons) Statistics', 'STA')
        ],
        'Faculty of Computing, Engineering and Technology': [
            ('Computer Science', 'B.Sc. (Hons) Computer Science', 'CSC'),
            ('Computer Science', 'B.Sc. (Hons) Cyber Security', 'CYB'),
            ('Computer Science', 'B.Sc. (Hons) Software Engineering', 'SEN'),
            ('Data Science', 'B.Sc. (Hons) Information Systems', 'IFS')
        ],
        'Faculty of Law': [
            ('Law', 'LL.B. (Hons) Common Law', 'LAW'),
            ('Law', 'LL.B. (Hons) Common and Islamic Law', 'CIL')
        ],
        'Faculty of Health Sciences': [
            ('Public Health', 'B.Sc. (Hons) Public Health', 'PUH'),
            ('Medical Laboratory', 'BMLS Medical Laboratory Science', 'MLS'),
            ('Human Anatomy', 'B.Sc. (Hons) Human Anatomy', 'ANA'),
            ('Human Physiology', 'B.Sc. (Hons) Human Physiology', 'PHY')
        ],
        'Faculty of Nursing Sciences': [
            ('Nursing Science', 'B.NSc. Nursing Science', 'NSC')
        ],
        'College of Health Sciences': [
            ('Medicine', 'MB;BS Bachelor of Medicine, Bachelor of Surgery', 'MBB')
        ],
        'Faculty of Agriculture': [
            ('Agriculture', 'B.Agric Agriculture', 'AGR')
        ]
    }

    first_names = ['Aisha', 'Ibrahim', 'Fatima', 'Yusuf', 'Zainab', 'Abubakar', 'Maryam', 'Umar', 'Amina', 'Hassan', 'Chinedu', 'Oluwaseun', 'Ngozi', 'Adeola', 'Chukwudi', 'Nneka', 'Joy', 'Grace']
    last_names = ['Adeyemi', 'Okafor', 'Bello', 'Abdullahi', 'Ogunleye', 'Mohammed', 'Suleiman', 'Bakare', 'Danladi', 'Olawale', 'Okonkwo', 'Adeleke', 'Lawal', 'Balogun', 'Ajayi']
    years = ['21', '22', '23', '24', '25']

    # Generate 150 realistic students across ALL Al-Hikmah departments
    for i in range(1, 151):
        faculty = random.choice(list(faculties_data.keys()))
        dept_info = random.choice(faculties_data[faculty])
        dept = dept_info[0]
        prog = dept_info[1]
        code = dept_info[2]
        
        # Build a realistic Al-Hikmah Matric Number (e.g., 23/05MBB001)
        year = random.choice(years)
        middle_code = f"0{random.randint(1, 9)}"
        serial = f"{random.randint(1, 999):03d}"
        matric_no = f"{year}/{middle_code}{code}{serial}"
        
        name = f"{random.choice(last_names)}, {random.choice(first_names)}"
        
        # Medicine usually has 6 levels (100-600), others 4 or 5
        if code == 'MBB':
            level = random.choice([100, 200, 300, 400, 500, 600])
        else:
            level = random.choice([100, 200, 300, 400, 500])
            
        status = random.choice(['Registered', 'Failed: Outstanding Payment'])
        
        # Insert Student
        cursor.execute('INSERT INTO students VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', 
                       (matric_no, pin_hash, name, faculty, dept, prog, level, '2025/2026', status))
        
        # Insert Finances (MBBS, Nursing, and Law generally have higher fees)
        if 'Health' in faculty or 'Nursing' in faculty or 'Law' in faculty:
            billed = random.choice([1200000, 1500000, 1800000])
        elif 'Computing' in faculty or 'Natural' in faculty:
            billed = random.choice([600000, 750000, 850000])
        else:
            billed = random.choice([450000, 500000, 600000])
            
        paid = billed if status == 'Registered' else billed - random.choice([100000, 250000])
        balance = billed - paid
        clearance = 'Cleared' if status == 'Registered' else 'Not Cleared - Outstanding Balance'

        # Insert Finances Record
        cursor.execute('''
            INSERT INTO finances (matric_no, total_billed, amount_paid, balance, clearance_status)
            VALUES (?, ?, ?, ?, ?)
        ''', (matric_no, billed, paid, balance, clearance))
        
        cursor.execute('INSERT INTO payments_history VALUES (?, ?, ?, ?, ?, ?, ?)', 
                       (f'TXN-{year}-{random.randint(1000,9999)}-{i}', matric_no, 'Sundry & Tuition Fee', paid, f'2025-{random.randint(1,12):02d}-15', f'RCPT-{serial}-{i}', 'Successful'))
        
        # Insert Results
        cgpa = round(random.uniform(2.0, 4.9), 2)
        cursor.execute('INSERT INTO results (matric_no, session, semester, gpa, cgpa) VALUES (?, ?, ?, ?, ?)', 
                       (matric_no, '2024/2025', '2nd Semester', cgpa, cgpa))

    # Commit changes and close
    conn.commit()
    conn.close()
    
    print("\n✅ SUCCESS: University-Wide Database Generated!")
    print("🎓 150 Mock Students created across 10 Faculties and 30+ actual Al-Hikmah Departments.")
    print(f"🔐 Master Profile Preserved: {my_matric} | PIN: 1234\n")

if __name__ == "__main__":
    create_mock_database()