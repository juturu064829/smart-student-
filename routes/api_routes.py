from flask import Blueprint, jsonify, request
from models import db, Student, Faculty, Department, Course, Attendance, Result, Fee, Salary
from utils.decorators import login_required

api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

# --- STUDENTS APIs ---
@api_bp.route('/students', methods=['GET'])
def get_students():
    dept_id = request.args.get('department_id', type=int)
    course_id = request.args.get('course_id', type=int)
    query = Student.query
    if dept_id:
        query = query.filter_by(department_id=dept_id)
    if course_id:
        query = query.filter_by(course_id=course_id)
    students = query.all()
    return jsonify({'status': 'success', 'count': len(students), 'data': [s.to_dict() for s in students]})

@api_bp.route('/students/<int:student_id>', methods=['GET'])
def get_student_by_id(student_id):
    student = Student.query.get_or_404(student_id)
    return jsonify({'status': 'success', 'data': student.to_dict()})

@api_bp.route('/students', methods=['POST'])
def create_student_api():
    data = request.json or {}
    required = ['roll_no', 'first_name', 'last_name', 'email', 'department_id', 'course_id']
    for field in required:
        if field not in data:
            return jsonify({'status': 'error', 'message': f'Missing required field: {field}'}), 400

    if Student.query.filter_by(roll_no=data['roll_no']).first():
        return jsonify({'status': 'error', 'message': 'Roll number already exists'}), 400

    student = Student(
        roll_no=data['roll_no'],
        first_name=data['first_name'],
        last_name=data['last_name'],
        gender=data.get('gender', 'Male'),
        email=data['email'],
        phone=data.get('phone'),
        department_id=data['department_id'],
        course_id=data['course_id'],
        current_year=data.get('current_year', 1),
        current_semester=data.get('current_semester', 1),
        status='Active'
    )
    db.session.add(student)
    db.session.commit()
    return jsonify({'status': 'success', 'message': 'Student created', 'data': student.to_dict()}), 201

@api_bp.route('/students/<int:student_id>', methods=['PUT'])
def update_student_api(student_id):
    student = Student.query.get_or_404(student_id)
    data = request.json or {}
    
    for key, value in data.items():
        if hasattr(student, key) and key not in ['id', 'roll_no']:
            setattr(student, key, value)

    db.session.commit()
    return jsonify({'status': 'success', 'message': 'Student updated', 'data': student.to_dict()})

@api_bp.route('/students/<int:student_id>', methods=['DELETE'])
def delete_student_api(student_id):
    student = Student.query.get_or_404(student_id)
    db.session.delete(student)
    db.session.commit()
    return jsonify({'status': 'success', 'message': f'Student ID {student_id} deleted'})

# --- FACULTY APIs ---
@api_bp.route('/faculty', methods=['GET'])
def get_faculty():
    faculty = Faculty.query.all()
    return jsonify({'status': 'success', 'count': len(faculty), 'data': [f.to_dict() for f in faculty]})

@api_bp.route('/faculty/<int:faculty_id>', methods=['GET'])
def get_faculty_by_id(faculty_id):
    fac = Faculty.query.get_or_404(faculty_id)
    return jsonify({'status': 'success', 'data': fac.to_dict()})

# --- DEPARTMENTS & COURSES APIs ---
@api_bp.route('/departments', methods=['GET'])
def get_departments():
    depts = Department.query.all()
    return jsonify({'status': 'success', 'count': len(depts), 'data': [d.to_dict() for d in depts]})

@api_bp.route('/courses', methods=['GET'])
def get_courses():
    courses = Course.query.all()
    return jsonify({'status': 'success', 'count': len(courses), 'data': [c.to_dict() for c in courses]})

# --- ATTENDANCE & RESULTS APIs ---
@api_bp.route('/attendance', methods=['GET'])
def get_attendance_api():
    student_id = request.args.get('student_id', type=int)
    query = Attendance.query
    if student_id:
        query = query.filter_by(student_id=student_id)
    records = query.limit(100).all()
    return jsonify({'status': 'success', 'count': len(records), 'data': [r.to_dict() for r in records]})

@api_bp.route('/results', methods=['GET'])
def get_results_api():
    student_id = request.args.get('student_id', type=int)
    query = Result.query
    if student_id:
        query = query.filter_by(student_id=student_id)
    records = query.all()
    return jsonify({'status': 'success', 'count': len(records), 'data': [r.to_dict() for r in records]})

# --- FEES & SALARIES APIs ---
@api_bp.route('/fees', methods=['GET'])
def get_fees_api():
    fees = Fee.query.all()
    return jsonify({'status': 'success', 'count': len(fees), 'data': [f.to_dict() for f in fees]})

@api_bp.route('/salaries', methods=['GET'])
def get_salaries_api():
    salaries = Salary.query.all()
    return jsonify({'status': 'success', 'count': len(salaries), 'data': [s.to_dict() for s in salaries]})
