from . import db, bcrypt


class Admin(db.Model):
    __tablename__ = 'admins'
    admin_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

class Lecturer(db.Model):
    __tablename__ = 'lecturers'
    lecturer_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def verify_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

class Student(db.Model):
    __tablename__ = 'students'
    student_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    registration_date = db.Column(db.Date)

class Exam(db.Model):
    __tablename__ = 'exams'
    exam_id = db.Column(db.Integer, primary_key=True)
    lecturer_id = db.Column(db.Integer, db.ForeignKey('lecturers.lecturer_id'))
    title = db.Column(db.String(255), nullable=False)
    exam_key = db.Column(db.String(255), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    is_active = db.Column(db.Boolean, default=True)

class Question(db.Model):
    __tablename__ = 'questions'
    question_id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.Integer, db.ForeignKey('exams.exam_id'))
    text = db.Column(db.Text, nullable=False)
    correct_answer = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.Enum('MCQ', 'SAQ'), nullable=False)
    options = db.Column(db.Text)  # JSON text for MCQ options

class StudentExamEnrollment(db.Model):
    __tablename__ = 'student_exam_enrollments'
    enrollment_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id'))
    exam_id = db.Column(db.Integer, db.ForeignKey('exams.exam_id'))
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    score = db.Column(db.Integer)

class Response(db.Model):
    __tablename__ = 'responses'
    response_id = db.Column(db.Integer, primary_key=True)
    enrollment_id = db.Column(db.Integer, db.ForeignKey('student_exam_enrollments.enrollment_id'))
    question_id = db.Column(db.Integer, db.ForeignKey('questions.question_id'))
    student_answer = db.Column(db.Text)
    is_correct = db.Column(db.Boolean)
    score = db.Column(db.Integer)  # Score is applicable for SAQ grading

class ExamResult(db.Model):
    __tablename__ = 'exam_results'
    result_id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.Integer, db.ForeignKey('exams.exam_id'))
    lecturer_id = db.Column(db.Integer, db.ForeignKey('lecturers.lecturer_id'))
    normal_distribution = db.Column(db.Text)  # JSON or TEXT format for distribution data
