import sqlite3
from werkzeug.security import generate_password_hash
import random

GRADE_SCALE = [
    (70, 100, 'A',  5.0),
    (60,  69, 'B',  4.0),
    (50,  59, 'C',  3.0),
    (45,  49, 'D',  2.0),
    (40,  44, 'E',  1.0),
    ( 0,  39, 'F',  0.0),
]

def score_to_grade(score):
    for low, high, letter, point in GRADE_SCALE:
        if low <= score <= high:
            return letter, point
    return 'F', 0.0

def compute_gpa(course_grades):
    """course_grades: list of (units, grade_point)"""
    total_units  = sum(u for u, _ in course_grades)
    total_points = sum(u * gp for u, gp in course_grades)
    if total_units == 0:
        return 0.0
    return round(total_points / total_units, 2)

COURSE_POOL = {
    '1st Semester': [
        ('GST101', 'Use of English I',               2),
        ('GST103', 'Nigerian Peoples and Culture',   2),
        ('CSC201', 'Introduction to Programming',    3),
        ('CSC301', 'Data Structures & Algorithms',   3),
        ('CYB301', 'Network Security Fundamentals',  3),
        ('CYB401', 'Ethical Hacking',                3),
        ('SEN201', 'Software Engineering Principles',3),
        ('ACC201', 'Financial Accounting I',         3),
        ('ECO201', 'Microeconomics',                 3),
        ('LAW201', 'Law of Contract I',              4),
        ('MCB301', 'Microbiology Techniques',        3),
        ('PUH201', 'Public Health Fundamentals',     3),
        ('NSC301', 'Nursing Practice I',             4),
        ('AGR201', 'Crop Science',                   3),
        ('ENG201', 'Literature in English I',        3),
        ('PHY201', 'Human Physiology I',             3),
        ('BUS301', 'Business Management',            3),
        ('MLS301', 'Haematology I',                  3),
        ('STA201', 'Probability & Statistics',       3),
        ('IFS201', 'Database Management Systems',    3),
    ],
    '2nd Semester': [
        ('GST102', 'Use of English II',              2),
        ('GST104', 'History of Islam',               2),
        ('CSC202', 'Object Oriented Programming',    3),
        ('CSC302', 'Computer Architecture',          3),
        ('CYB302', 'Cryptography',                   3),
        ('CYB402', 'Digital Forensics',              3),
        ('SEN202', 'Software Testing & QA',          3),
        ('ACC202', 'Financial Accounting II',        3),
        ('ECO202', 'Macroeconomics',                 3),
        ('LAW202', 'Law of Tort',                    4),
        ('MCB302', 'Virology',                       3),
        ('PUH202', 'Epidemiology',                   3),
        ('NSC302', 'Nursing Practice II',            4),
        ('AGR202', 'Soil Science',                   3),
        ('ENG202', 'Literature in English II',       3),
        ('PHY202', 'Human Physiology II',            3),
        ('BUS302', 'Organisational Behaviour',       3),
        ('MLS302', 'Haematology II',                 3),
        ('STA202', 'Statistical Inference',          3),
        ('IFS202', 'Systems Analysis & Design',      3),
    ],
}

SESSIONS = ['2023/2024', '2024/2025', '2025/2026']
SEMESTERS = ['1st Semester', '2nd Semester']


def create_mock_database():
    conn   = sqlite3.connect('university.db')
    cursor = conn.cursor()

    # Drop all tables cleanly
    for table in ['students', 'finances', 'payments_history',
                  'course_registration', 'course_grades',
                  'accommodation', 'results']:
        cursor.execute(f'DROP TABLE IF EXISTS {table}')

    # 1. Students
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

    # 2. Finances
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

    # 3. Payments History
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

    # 4. Course Registration
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

    # 5. Course Grades (NEW — per course, per semester)
    cursor.execute('''
        CREATE TABLE course_grades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            matric_no TEXT,
            course_code TEXT,
            course_title TEXT,
            units INTEGER,
            score INTEGER,
            grade TEXT,
            grade_point REAL,
            semester TEXT,
            session TEXT,
            FOREIGN KEY(matric_no) REFERENCES students(matric_no)
        )
    ''')

    # 6. Accommodation
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

    # 7. Results (summary per semester)
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
    # MASTER PROFILE — Lawal, Muheebdeen Ayodeji
    # =========================================================
    pin_hash  = generate_password_hash("1234")
    my_matric = "22/03CYB059"

    cursor.execute('INSERT INTO students VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
        (my_matric, pin_hash, 'Lawal, Muheebdeen Ayodeji',
         'Faculty of Computing, Engineering and Technology',
         'Computer Science', 'B.Sc. (Hons) Cyber Security',
         400, '2025/2026', 'Failed: Outstanding Payment'))

    cursor.execute('INSERT INTO finances (matric_no, total_billed, amount_paid, balance, clearance_status) VALUES (?, ?, ?, ?, ?)',
        (my_matric, 850000, 150000, 700000, 'Not Cleared - Outstanding Balance'))

    cursor.execute('INSERT INTO payments_history VALUES (?, ?, ?, ?, ?, ?, ?)',
        ('TXN-2025-9981', my_matric, 'Sundry Fee', 150000.00, '2025-11-15', 'RCPT-1102A', 'Successful'))

    cursor.execute('INSERT INTO accommodation (matric_no, hostel_name, room_number, status) VALUES (?, ?, ?, ?)',
        (my_matric, 'Male Hostel A', 'Room 42B', 'Allocated'))

    # Master profile: courses + grades across 2 sessions x 2 semesters
    master_courses = {
        ('2023/2024', '1st Semester'): [
            ('CSC201', 'Introduction to Programming',    3),
            ('GST101', 'Use of English I',               2),
            ('GST103', 'Nigerian Peoples and Culture',   2),
            ('STA201', 'Probability & Statistics',       3),
            ('IFS201', 'Database Management Systems',    3),
        ],
        ('2023/2024', '2nd Semester'): [
            ('CSC202', 'Object Oriented Programming',    3),
            ('GST102', 'Use of English II',              2),
            ('GST104', 'History of Islam',               2),
            ('CYB302', 'Cryptography',                   3),
            ('IFS202', 'Systems Analysis & Design',      3),
        ],
        ('2024/2025', '1st Semester'): [
            ('CYB301', 'Network Security Fundamentals',  3),
            ('CYB401', 'Ethical Hacking',                3),
            ('CSC301', 'Data Structures & Algorithms',   3),
            ('SEN201', 'Software Engineering Principles',3),
        ],
        ('2024/2025', '2nd Semester'): [
            ('CYB402', 'Digital Forensics',              3),
            ('CSC302', 'Computer Architecture',          3),
            ('SEN202', 'Software Testing & QA',          3),
        ],
        ('2025/2026', '1st Semester'): [
            ('CYB405', 'Advanced Network Security',      3),
            ('CYB403', 'Malware Analysis',               3),
            ('CSC401', 'Artificial Intelligence',        3),
            ('SEN301', 'Agile Software Development',     3),
        ],
        ('2025/2026', '2nd Semester'): [
            ('CYB406', 'Cloud Security',                 3),
            ('CYB404', 'Cyber Law & Ethics',             3),
            ('CSC402', 'Machine Learning',               3),
        ],
    }

    # Define master scores (good student, 400 level)
    master_scores = {
        'CSC201': 78, 'GST101': 72, 'GST103': 68, 'STA201': 75, 'IFS201': 80,
        'CSC202': 82, 'GST102': 74, 'GST104': 70, 'CYB302': 85, 'IFS202': 77,
        'CYB301': 88, 'CYB401': 90, 'CSC301': 83, 'SEN201': 79,
        'CYB402': 87, 'CSC302': 81, 'SEN202': 84,
        'CYB405': 92, 'CYB403': 89, 'CSC401': 85, 'SEN301': 88,
        'CYB406': 90, 'CYB404': 86, 'CSC402': 91,
    }

    all_gpa = []
    for (sess, sem), courses in master_courses.items():
        sem_grades = []
        for (code, title, units) in courses:
            # Register course
            cursor.execute('''
                INSERT INTO course_registration (matric_no, course_code, course_title, units, semester, session, extra_unit_status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (my_matric, code, title, units, sem, sess, 'N/A'))

            score = master_scores.get(code, random.randint(60, 90))
            letter, gp = score_to_grade(score)

            cursor.execute('''
                INSERT INTO course_grades (matric_no, course_code, course_title, units, score, grade, grade_point, semester, session)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (my_matric, code, title, units, score, letter, gp, sem, sess))

            sem_grades.append((units, gp))

        gpa = compute_gpa(sem_grades)
        all_gpa.append(gpa)
        cgpa = round(sum(all_gpa) / len(all_gpa), 2)

        cursor.execute('''
            INSERT INTO results (matric_no, session, semester, gpa, cgpa)
            VALUES (?, ?, ?, ?, ?)
        ''', (my_matric, sess, sem, gpa, cgpa))

    # =========================================================
    # GENERATE 150 MOCK STUDENTS
    # =========================================================
    faculties_data = {
        'Faculty of Humanities and Social Sciences': [
            ('History and International Studies', 'B.A (Hons) History and International Relations', 'HIR'),
            ('Islamic Studies', 'B.A (Hons) Islamic Studies', 'ISS'),
            ('Languages', 'B.A (Hons) English', 'ENG'),
            ('Languages', 'B.A (Hons) Arabic', 'ARA'),
            ('Mass Communication', 'B.Sc. (Hons) Mass Communication', 'MAC'),
            ('Political and Public Administration', 'B.Sc. (Hons) Political Science', 'POL'),
            ('Sociology', 'B.Sc. (Hons) Sociology', 'SOC'),
        ],
        'Faculty of Management Sciences': [
            ('Accounting', 'B.Sc. (Hons) Accounting', 'ACC'),
            ('Banking and Finance', 'B.Sc. (Hons) Banking and Finance', 'BNK'),
            ('Business Administration', 'B.Sc. (Hons) Business Administration', 'BUS'),
            ('Economics', 'B.Sc. (Hons) Economics', 'ECO'),
        ],
        'Faculty of Education': [
            ('Education Management', 'B.Ed. Educational Management', 'EDM'),
            ('Science Education', 'B.Sc. (Ed.) Computer Science', 'EDS'),
            ('Arts and Social Science Education', 'B.A. (Ed.) English', 'EDA'),
            ('Library and Information Science', 'BLIS Library and Information Science', 'LIS'),
        ],
        'Faculty of Natural and Applied Sciences': [
            ('Biological Sciences', 'B.Sc. (Hons) Microbiology', 'MCB'),
            ('Biological Sciences', 'B.Sc. (Hons) Biochemistry', 'BCH'),
            ('Chemical and Geological Sciences', 'B.Sc. (Hons) Industrial Chemistry', 'ICH'),
            ('Physical Sciences', 'B.Sc. (Hons) Statistics', 'STA'),
        ],
        'Faculty of Computing, Engineering and Technology': [
            ('Computer Science', 'B.Sc. (Hons) Computer Science', 'CSC'),
            ('Computer Science', 'B.Sc. (Hons) Cyber Security', 'CYB'),
            ('Computer Science', 'B.Sc. (Hons) Software Engineering', 'SEN'),
            ('Data Science', 'B.Sc. (Hons) Information Systems', 'IFS'),
        ],
        'Faculty of Law': [
            ('Law', 'LL.B. (Hons) Common Law', 'LAW'),
            ('Law', 'LL.B. (Hons) Common and Islamic Law', 'CIL'),
        ],
        'Faculty of Health Sciences': [
            ('Public Health', 'B.Sc. (Hons) Public Health', 'PUH'),
            ('Medical Laboratory', 'BMLS Medical Laboratory Science', 'MLS'),
            ('Human Anatomy', 'B.Sc. (Hons) Human Anatomy', 'ANA'),
            ('Human Physiology', 'B.Sc. (Hons) Human Physiology', 'PHY'),
        ],
        'Faculty of Nursing Sciences': [
            ('Nursing Science', 'B.NSc. Nursing Science', 'NSC'),
        ],
        'College of Health Sciences': [
            ('Medicine', 'MB;BS Bachelor of Medicine, Bachelor of Surgery', 'MBB'),
        ],
        'Faculty of Agriculture': [
            ('Agriculture', 'B.Agric Agriculture', 'AGR'),
        ],
    }

    first_names = ['Aisha', 'Ibrahim', 'Fatima', 'Yusuf', 'Zainab', 'Abubakar',
                   'Maryam', 'Umar', 'Amina', 'Hassan', 'Chinedu', 'Oluwaseun',
                   'Ngozi', 'Adeola', 'Chukwudi', 'Nneka', 'Joy', 'Grace']
    last_names  = ['Adeyemi', 'Okafor', 'Bello', 'Abdullahi', 'Ogunleye',
                   'Mohammed', 'Suleiman', 'Bakare', 'Danladi', 'Olawale',
                   'Okonkwo', 'Adeleke', 'Lawal', 'Balogun', 'Ajayi']
    years = ['21', '22', '23', '24', '25']

    for i in range(1, 151):
        faculty   = random.choice(list(faculties_data.keys()))
        dept_info = random.choice(faculties_data[faculty])
        dept, prog, code = dept_info

        year       = random.choice(years)
        mid        = f"0{random.randint(1,9)}"
        serial     = f"{random.randint(1,999):03d}"
        matric_no  = f"{year}/{mid}{code}{serial}"
        name       = f"{random.choice(last_names)}, {random.choice(first_names)}"
        level      = random.choice([100,200,300,400,500,600] if code=='MBB' else [100,200,300,400,500])
        status     = random.choice(['Registered', 'Failed: Outstanding Payment'])

        cursor.execute('INSERT INTO students VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (matric_no, pin_hash, name, faculty, dept, prog, level, '2025/2026', status))

        # Finances
        if 'Health' in faculty or 'Nursing' in faculty or 'Law' in faculty:
            billed = random.choice([1200000, 1500000, 1800000])
        elif 'Computing' in faculty or 'Natural' in faculty:
            billed = random.choice([600000, 750000, 850000])
        else:
            billed = random.choice([450000, 500000, 600000])

        paid     = billed if status == 'Registered' else billed - random.choice([100000, 250000])
        balance  = billed - paid
        clearance = 'Cleared' if status == 'Registered' else 'Not Cleared - Outstanding Balance'

        cursor.execute('''
            INSERT INTO finances (matric_no, total_billed, amount_paid, balance, clearance_status)
            VALUES (?, ?, ?, ?, ?)
        ''', (matric_no, billed, paid, balance, clearance))

        cursor.execute('INSERT INTO payments_history VALUES (?, ?, ?, ?, ?, ?, ?)',
            (f'TXN-{year}-{random.randint(1000,9999)}-{i}', matric_no,
             'Sundry & Tuition Fee', paid,
             f'2025-{random.randint(1,12):02d}-15',
             f'RCPT-{serial}-{i}', 'Successful'))

        # Accommodation
        if random.random() < 0.70:
            hostel = random.choice(['Male Hostel A', 'Male Hostel B', 'Female Hostel A', 'Female Hostel D'])
            room   = f"Room {random.randint(1,50)}{random.choice(['A','B','C'])}"
            cursor.execute('INSERT INTO accommodation (matric_no, hostel_name, room_number, status) VALUES (?, ?, ?, ?)',
                (matric_no, hostel, room, 'Allocated'))
        else:
            cursor.execute('INSERT INTO accommodation (matric_no, hostel_name, room_number, status) VALUES (?, ?, ?, ?)',
                (matric_no, 'N/A', 'N/A', 'Not Allocated - Apply on the portal'))

        # Courses + Grades across 2 sessions x 2 semesters
        all_gpa_list = []
        for sess in SESSIONS:
            for sem in SEMESTERS:
                pool     = COURSE_POOL[sem]
                chosen   = random.sample(pool, random.randint(3, 5))
                sem_list = []
                for (ccode, ctitle, cunits) in chosen:
                    cursor.execute('''
                        INSERT INTO course_registration
                        (matric_no, course_code, course_title, units, semester, session, extra_unit_status)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (matric_no, ccode, ctitle, cunits, sem, sess, 'N/A'))

                    score        = random.randint(30, 95)
                    letter, gp   = score_to_grade(score)
                    cursor.execute('''
                        INSERT INTO course_grades
                        (matric_no, course_code, course_title, units, score, grade, grade_point, semester, session)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (matric_no, ccode, ctitle, cunits, score, letter, gp, sem, sess))
                    sem_list.append((cunits, gp))

                gpa = compute_gpa(sem_list)
                all_gpa_list.append(gpa)
                cgpa = round(sum(all_gpa_list) / len(all_gpa_list), 2)
                cursor.execute('''
                    INSERT INTO results (matric_no, session, semester, gpa, cgpa)
                    VALUES (?, ?, ?, ?, ?)
                ''', (matric_no, sess, sem, gpa, cgpa))

    conn.commit()
    conn.close()
    print("\n✅ SUCCESS: University-Wide Database Generated!")
    print("🎓 150 Mock Students created with full multi-semester course grades.")
    print(f"🔐 Master Profile Preserved: {my_matric} | PIN: 1234\n")

if __name__ == "__main__":
    create_mock_database()