import random
from datetime import datetime, date, timedelta
import os
import sys

# Add parent directory to sys.path to enable imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from models import (
    db, User, Department, Course, Subject, Faculty, 
    Student, Attendance, Result, Fee, Salary, Timetable, 
    Announcement, Notification
)

FIRST_NAMES = [
    "Aarav", "Ananya", "Rohan", "Priya", "Aditya", "Sneha", "Vikram", "Neha",
    "Rahul", "Kavya", "Siddharth", "Pooja", "Arjun", "Isha", "Karan", "Diya",
    "Manish", "Riya", "Aman", "Simran", "Varun", "Tanvi", "Nikhil", "Shreya",
    "Akash", "Anushka", "Dev", "Meera", "Yash", "Tara", "Sameer", "Nisha",
    "Harsh", "Deepika", "Kunal", "Swati", "Raj", "Nandini", "Amit", "Kirti"
]

LAST_NAMES = [
    "Sharma", "Verma", "Gupta", "Patel", "Singh", "Kumar", "Reddy", "Rao",
    "Joshi", "Mehta", "Nair", "Iyer", "Chopra", "Malhotra", "Bhasin", "Deshmukh",
    "Kulkarni", "Chaudhary", "Kapoor", "Bhatt", "Saxena", "Agarwal", "Dutta", "Das"
]

CITIES = ["Mumbai", "Delhi", "Bengaluru", "Hyderabad", "Chennai", "Pune", "Kolkata", "Ahmedabad", "Jaipur", "Lucknow"]
STATES = ["Maharashtra", "Delhi", "Karnataka", "Telangana", "Tamil Nadu", "West Bengal", "Gujarat", "Rajasthan", "Uttar Pradesh"]
BLOOD_GROUPS = ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"]

def seed_database():
    with app.app_context():
        print("Recreating database tables...")
        db.drop_all()
        db.create_all()

        print("1. Creating System Admin...")
        admin = User(
            username='admin',
            email='admin@smartcollege.edu',
            role='Admin',
            status='Active'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()

        print("2. Creating Departments...")
        departments_data = [
            {"code": "CSE", "name": "Computer Science & Engineering", "hod": "Dr. Ramesh Kumar", "email": "cse.hod@smartcollege.edu", "phone": "+91 9876543210", "desc": "Focuses on computer systems, software engineering, AI, and cybersecurity."},
            {"code": "ECE", "name": "Electronics & Communication Eng.", "hod": "Dr. Sunita Sharma", "email": "ece.hod@smartcollege.edu", "phone": "+91 9876543211", "desc": "Deals with semiconductor design, signal processing, and communication networks."},
            {"code": "MECH", "name": "Mechanical Engineering", "hod": "Dr. Anil Verma", "email": "mech.hod@smartcollege.edu", "phone": "+91 9876543212", "desc": "Covers thermodynamics, robotics, manufacturing systems, and CAD design."},
            {"code": "CIVIL", "name": "Civil Engineering", "hod": "Dr. Pradeep Gupta", "email": "civil.hod@smartcollege.edu", "phone": "+91 9876543213", "desc": "Focuses on structural engineering, urban infrastructure, and environmental tech."},
            {"code": "MBA", "name": "Department of Business Administration", "hod": "Dr. Meenakshi Sundaram", "email": "mba.hod@smartcollege.edu", "phone": "+91 9876543214", "desc": "Specializes in marketing, corporate finance, HR, and strategic management."}
        ]
        
        dept_objs = []
        for d in departments_data:
            dept = Department(
                code=d["code"],
                name=d["name"],
                hod_name=d["hod"],
                email=d["email"],
                phone=d["phone"],
                description=d["desc"],
                status='Active'
            )
            db.session.add(dept)
            dept_objs.append(dept)
        db.session.commit()

        print("3. Creating Courses...")
        courses_data = [
            {"code": "BTECH-CSE", "name": "B.Tech Computer Science & Engineering", "dept_idx": 0, "years": 4, "sems": 8, "credits": 160},
            {"code": "BTECH-ECE", "name": "B.Tech Electronics & Communication", "dept_idx": 1, "years": 4, "sems": 8, "credits": 160},
            {"code": "BTECH-MECH", "name": "B.Tech Mechanical Engineering", "dept_idx": 2, "years": 4, "sems": 8, "credits": 160},
            {"code": "BTECH-CIVIL", "name": "B.Tech Civil Engineering", "dept_idx": 3, "years": 4, "sems": 8, "credits": 160},
            {"code": "MBA-GEN", "name": "Master of Business Administration", "dept_idx": 4, "years": 2, "sems": 4, "credits": 90}
        ]
        
        course_objs = []
        for c in courses_data:
            course = Course(
                code=c["code"],
                name=c["name"],
                department_id=dept_objs[c["dept_idx"]].id,
                duration_years=c["years"],
                total_semesters=c["sems"],
                credits=c["credits"],
                description=f"Standard academic degree program for {c['name']}.",
                status='Active'
            )
            db.session.add(course)
            course_objs.append(course)
        db.session.commit()

        print("4. Creating Subjects...")
        subjects_data = [
            # CSE Subjects
            {"code": "CS101", "name": "Data Structures & Algorithms", "c_idx": 0, "sem": 1},
            {"code": "CS102", "name": "Database Management Systems", "c_idx": 0, "sem": 2},
            {"code": "CS201", "name": "Operating Systems", "c_idx": 0, "sem": 3},
            {"code": "CS202", "name": "Computer Networks", "c_idx": 0, "sem": 4},
            {"code": "CS301", "name": "Artificial Intelligence & ML", "c_idx": 0, "sem": 5},
            # ECE Subjects
            {"code": "EC101", "name": "Digital Electronics", "c_idx": 1, "sem": 1},
            {"code": "EC102", "name": "Microprocessors & Microcontrollers", "c_idx": 1, "sem": 2},
            {"code": "EC201", "name": "Signals & Systems", "c_idx": 1, "sem": 3},
            {"code": "EC202", "name": "VLSI Design", "c_idx": 1, "sem": 4},
            {"code": "EC301", "name": "Wireless Communication", "c_idx": 1, "sem": 5},
            # MECH Subjects
            {"code": "ME101", "name": "Engineering Thermodynamics", "c_idx": 2, "sem": 1},
            {"code": "ME102", "name": "Fluid Mechanics", "c_idx": 2, "sem": 2},
            {"code": "ME201", "name": "Theory of Machines", "c_idx": 2, "sem": 3},
            {"code": "ME202", "name": "Heat & Mass Transfer", "c_idx": 2, "sem": 4},
            # CIVIL Subjects
            {"code": "CE101", "name": "Structural Analysis", "c_idx": 3, "sem": 1},
            {"code": "CE102", "name": "Concrete Technology", "c_idx": 3, "sem": 2},
            {"code": "CE201", "name": "Geotechnical Engineering", "c_idx": 3, "sem": 3},
            # MBA Subjects
            {"code": "MB101", "name": "Financial Accounting", "c_idx": 4, "sem": 1},
            {"code": "MB102", "name": "Marketing Management", "c_idx": 4, "sem": 1},
            {"code": "MB201", "name": "Human Resource Strategy", "c_idx": 4, "sem": 2},
            {"code": "MB202", "name": "Operations & Supply Chain", "c_idx": 4, "sem": 2}
        ]

        subj_objs = []
        for s in subjects_data:
            subj = Subject(
                code=s["code"],
                name=s["name"],
                course_id=course_objs[s["c_idx"]].id,
                semester=s["sem"],
                credits=4,
                max_internal=20.0,
                max_assignment=10.0,
                max_practical=20.0,
                max_external=50.0
            )
            db.session.add(subj)
            subj_objs.append(subj)
        db.session.commit()

        print("5. Creating 20 Faculty Members & Accounts...")
        faculty_objs = []
        designations = ["Professor", "Associate Professor", "Assistant Professor", "Senior Lecturer"]
        qualifications = ["Ph.D. in Computer Science", "Ph.D. in VLSI", "M.Tech in Thermal Eng", "Ph.D. in Management", "M.Tech in Structural Eng"]
        
        fac_count = 1
        for d_idx, dept in enumerate(dept_objs):
            for i in range(4):  # 4 faculty per department
                fname = random.choice(FIRST_NAMES)
                lname = random.choice(LAST_NAMES)
                emp_id = f"FAC{2025000 + fac_count:04d}"
                email = f"faculty{fac_count}@smartcollege.edu"
                username = f"faculty{fac_count}"
                
                fac = Faculty(
                    emp_id=emp_id,
                    first_name=fname,
                    last_name=lname,
                    gender=random.choice(["Male", "Female"]),
                    email=email,
                    phone=f"+91 987{random.randint(1000000, 9999999)}",
                    department_id=dept.id,
                    designation=random.choice(designations),
                    qualification=random.choice(qualifications),
                    joining_date=date(2018 + random.randint(0, 5), random.randint(1, 12), random.randint(1, 28)),
                    experience_years=random.randint(3, 18),
                    basic_salary=random.choice([60000, 75000, 90000, 110000]),
                    address=f"Flat {random.randint(101, 909)}, Academic Block, Campus Area",
                    status='Active'
                )
                db.session.add(fac)
                db.session.flush()

                # User Account for Faculty
                f_user = User(
                    username=username,
                    email=email,
                    role='Faculty',
                    status='Active',
                    faculty_id=fac.id
                )
                f_user.set_password('faculty123')
                db.session.add(f_user)
                
                faculty_objs.append(fac)
                fac_count += 1
        db.session.commit()

        print("6. Creating 105 Students & Accounts...")
        student_objs = []
        stu_count = 1
        
        for d_idx, dept in enumerate(dept_objs):
            # Pick primary course for department
            course = course_objs[d_idx]
            for i in range(21):  # 21 students per department = 105 total
                fname = random.choice(FIRST_NAMES)
                lname = random.choice(LAST_NAMES)
                roll_no = f"STU2025{stu_count:03d}"
                email = f"student{stu_count}@smartcollege.edu"
                username = f"student{stu_count}"
                
                year = (i % course.duration_years) + 1
                sem = ((year - 1) * 2) + random.choice([1, 2])
                
                stu = Student(
                    roll_no=roll_no,
                    first_name=fname,
                    last_name=lname,
                    gender=random.choice(["Male", "Female"]),
                    dob=date(2002 + random.randint(0, 4), random.randint(1, 12), random.randint(1, 28)),
                    email=email,
                    phone=f"+91 912{random.randint(1000000, 9999999)}",
                    address=f"Street {random.randint(1, 50)}, Sector {random.randint(1, 25)}",
                    city=random.choice(CITIES),
                    state=random.choice(STATES),
                    department_id=dept.id,
                    course_id=course.id,
                    current_year=year,
                    current_semester=sem,
                    admission_date=date(2025 - year, 8, 1),
                    guardian_name=f"Mr. {random.choice(LAST_NAMES)}",
                    guardian_phone=f"+91 944{random.randint(1000000, 9999999)}",
                    blood_group=random.choice(BLOOD_GROUPS),
                    status='Active'
                )
                db.session.add(stu)
                db.session.flush()

                # User account for student
                s_user = User(
                    username=username,
                    email=email,
                    role='Student',
                    status='Active',
                    student_id=stu.id
                )
                s_user.set_password('student123')
                db.session.add(s_user)

                student_objs.append(stu)
                stu_count += 1
        db.session.commit()

        print("7. Seeding Attendance Records (1200+ logs)...")
        # Create attendance logs for past 15 working days
        today = date.today()
        working_days = [today - timedelta(days=i) for i in range(25) if (today - timedelta(days=i)).weekday() < 5][:15]
        
        for stu in student_objs:
            # Determine baseline attendance profile (some students have low attendance to test risk engine)
            base_prob = random.choice([0.95, 0.90, 0.85, 0.70, 0.55])  # 0.55/0.70 will trigger risk alert
            for day in working_days:
                rand_val = random.random()
                if rand_val < base_prob:
                    status = 'Present'
                elif rand_val < base_prob + 0.05:
                    status = 'Late'
                elif rand_val < base_prob + 0.10:
                    status = 'Leave'
                else:
                    status = 'Absent'

                # Pick relevant subject
                course_subjs = [s for s in subj_objs if s.course_id == stu.course_id]
                subj = random.choice(course_subjs) if course_subjs else subj_objs[0]
                fac = faculty_objs[0]

                att = Attendance(
                    student_id=stu.id,
                    course_id=stu.course_id,
                    subject_id=subj.id,
                    date=day,
                    status=status,
                    marked_by_faculty_id=fac.id,
                    remarks="Regular Class Session" if status == 'Present' else f"Recorded as {status}"
                )
                db.session.add(att)
        db.session.commit()

        print("8. Seeding Exam Results (300+ marks)...")
        for stu in student_objs:
            course_subjs = [s for s in subj_objs if s.course_id == stu.course_id]
            for subj in course_subjs:
                # Randomize performance to test risk engine
                is_weak = random.random() < 0.15
                if is_weak:
                    internal = round(random.uniform(5.0, 10.0), 1)
                    assignment = round(random.uniform(2.0, 5.0), 1)
                    practical = round(random.uniform(8.0, 12.0), 1)
                    external = round(random.uniform(10.0, 20.0), 1)
                else:
                    internal = round(random.uniform(14.0, 20.0), 1)
                    assignment = round(random.uniform(7.0, 10.0), 1)
                    practical = round(random.uniform(15.0, 20.0), 1)
                    external = round(random.uniform(30.0, 48.0), 1)

                res = Result(
                    student_id=stu.id,
                    subject_id=subj.id,
                    internal_marks=internal,
                    assignment_marks=assignment,
                    practical_marks=practical,
                    external_marks=external,
                    semester=subj.semester,
                    academic_year='2025-2026'
                )
                res.calculate_grade()
                db.session.add(res)
        db.session.commit()

        print("9. Seeding Fees Records...")
        for stu in student_objs:
            tuition = 45000.0
            exam = 2500.0
            library = 1500.0
            hostel = random.choice([0.0, 15000.0, 20000.0])
            other = 1000.0
            total = tuition + exam + library + hostel + other
            
            pay_type = random.choice(['Full', 'Partial', 'Pending'])
            if pay_type == 'Full':
                paid = total
                status = 'Paid'
                p_date = date.today() - timedelta(days=random.randint(10, 60))
            elif pay_type == 'Partial':
                paid = round(total * random.choice([0.4, 0.5, 0.6]), 2)
                status = 'Partially Paid'
                p_date = date.today() - timedelta(days=random.randint(5, 30))
            else:
                paid = 0.0
                status = 'Pending'
                p_date = None

            fee = Fee(
                student_id=stu.id,
                tuition_fee=tuition,
                exam_fee=exam,
                library_fee=library,
                hostel_fee=hostel,
                other_fee=other,
                total_fee=total,
                paid_amount=paid,
                pending_amount=max(0.0, total - paid),
                payment_date=p_date,
                payment_status=status,
                remarks="Academic Year 2025-26 Fees"
            )
            db.session.add(fee)
        db.session.commit()

        print("10. Seeding Faculty Payroll / Salaries...")
        months = ["July", "August"]
        for fac in faculty_objs:
            for m in months:
                basic = fac.basic_salary
                allowances = round(basic * 0.10, 2)
                bonus = 2000.0 if m == "August" else 0.0
                deductions = round(basic * 0.05, 2)
                net = basic + allowances + bonus - deductions
                
                status = 'Paid' if m == "July" else random.choice(['Paid', 'Pending'])
                p_date = date(2026, 7, 31) if m == "July" else (date(2026, 8, 5) if status == 'Paid' else None)

                sal = Salary(
                    faculty_id=fac.id,
                    basic_salary=basic,
                    allowances=allowances,
                    bonus=bonus,
                    deductions=deductions,
                    net_salary=net,
                    payment_date=p_date,
                    payment_status=status,
                    month=m,
                    year=2026,
                    payment_method='Direct Bank Transfer'
                )
                db.session.add(sal)
        db.session.commit()

        print("11. Seeding Timetable Slots...")
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        slots = [("09:00 AM", "10:00 AM"), ("10:00 AM", "11:00 AM"), ("11:15 AM", "12:15 PM"), ("01:30 PM", "02:30 PM")]
        rooms = ["Lecture Hall A-101", "Lab B-204", "Seminar Room C-301", "Auditorium D"]

        for d_idx, dept in enumerate(dept_objs):
            course = course_objs[d_idx]
            c_subjs = [s for s in subj_objs if s.course_id == course.id]
            d_facs = [f for f in faculty_objs if f.department_id == dept.id]
            
            if c_subjs and d_facs:
                for day_i, day in enumerate(days):
                    subj = c_subjs[day_i % len(c_subjs)]
                    fac = d_facs[day_i % len(d_facs)]
                    time_slot = slots[day_i % len(slots)]
                    
                    tt = Timetable(
                        department_id=dept.id,
                        course_id=course.id,
                        subject_id=subj.id,
                        faculty_id=fac.id,
                        room_number=random.choice(rooms),
                        day_of_week=day,
                        start_time=time_slot[0],
                        end_time=time_slot[1],
                        semester=subj.semester
                    )
                    db.session.add(tt)
        db.session.commit()

        print("12. Seeding Announcements & Notifications...")
        announcements_data = [
            {"title": "Mid-Term Semester Examination Schedule Released", "content": "The official timetable for Mid-Term examinations for all B.Tech and MBA courses is now live on the portal. Exams start from Sept 1st.", "role": "All", "cat": "Exam", "prio": "High"},
            {"title": "Annual Campus Tech Symposium 2026", "content": "Registration for paper presentations and robotics hackathon is open until August 25th. All students are encouraged to participate.", "role": "Student", "cat": "Academic", "prio": "Normal"},
            {"title": "Faculty Departmental Meeting Notice", "content": "All Department HODs and faculty members are requested to attend the monthly academic evaluation meeting in the Senate Hall.", "role": "Faculty", "cat": "General", "prio": "High"},
            {"title": "Important Fee Payment Deadline Reminder", "content": "Students with pending fee balances are advised to clear outstanding amounts by August 20th to avoid late payment fines.", "role": "Student", "cat": "Fee", "prio": "Urgent"}
        ]
        for a in announcements_data:
            ann = Announcement(
                title=a["title"],
                content=a["content"],
                target_role=a["role"],
                category=a["cat"],
                priority=a["prio"],
                created_by_user_id=admin.id
            )
            db.session.add(ann)
        db.session.commit()

        print("Database Seeding Completed Successfully!")
        print("--------------------------------------------------")
        print("DEMO CREDENTIALS:")
        print("Admin:   username: admin    / password: admin123")
        print("Faculty: username: faculty1 / password: faculty123 (to faculty20)")
        print("Student: username: student1 / password: student123 (to student105)")
        print("--------------------------------------------------")

if __name__ == '__main__':
    seed_database()
