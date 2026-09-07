def calculate_grade_and_status(percentage):
    """
    Grading Scale:
    90 - 100: A+ (4.0) Pass
    80 - 89 : A  (3.7) Pass
    70 - 79 : B+ (3.3) Pass
    60 - 69 : B  (3.0) Pass
    50 - 59 : C  (2.5) Pass
    40 - 49 : D  (2.0) Pass
    Below 40: F  (0.0) Fail
    """
    if percentage >= 90.0:
        return {'grade': 'A+', 'grade_point': 4.0, 'status': 'Pass'}
    elif percentage >= 80.0:
        return {'grade': 'A', 'grade_point': 3.7, 'status': 'Pass'}
    elif percentage >= 70.0:
        return {'grade': 'B+', 'grade_point': 3.3, 'status': 'Pass'}
    elif percentage >= 60.0:
        return {'grade': 'B', 'grade_point': 3.0, 'status': 'Pass'}
    elif percentage >= 50.0:
        return {'grade': 'C', 'grade_point': 2.5, 'status': 'Pass'}
    elif percentage >= 40.0:
        return {'grade': 'D', 'grade_point': 2.0, 'status': 'Pass'}
    else:
        return {'grade': 'F', 'grade_point': 0.0, 'status': 'Fail'}

def calculate_gpa(results):
    if not results:
        return 0.0
    total_points = 0.0
    count = 0
    for r in results:
        total_points += r.grade_point or 0.0
        count += 1
    return round(total_points / count, 2) if count > 0 else 0.0

def calculate_net_salary(basic, allowances=0.0, bonus=0.0, deductions=0.0):
    return (basic or 0.0) + (allowances or 0.0) + (bonus or 0.0) - (deductions or 0.0)

def calculate_pending_fee(total_fee, paid_amount):
    return max(0.0, (total_fee or 0.0) - (paid_amount or 0.0))
