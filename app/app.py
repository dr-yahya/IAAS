from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import hashlib  

app = Flask(__name__)
app.secret_key = 'your_secret_key'

DATABASE = 'iaasdb.sqlite'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn
def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()
def check_user(email, password, user_type='student'):
    table = 'students' if user_type == 'student' else 'admins'
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table} WHERE email = ? AND password = ?", (email, hashlib.md5(password.encode()).hexdigest()))
    user = cursor.fetchone()
    conn.close()
    return user

@app.route('/', methods=['GET', 'POST'])
def index():
    return redirect(url_for('register'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        # Validate the form data
        if not name or not email or not password:
            flash('Please fill out all fields', 'danger')
            return render_template('register.html')

        # Hash the password
        hashed_password = hashlib.md5(password.encode()).hexdigest()

        # Check if the email is already registered
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students WHERE email = ?", (email,))
        existing_user = cursor.fetchone()
        if existing_user:
            flash('Email is already registered', 'danger')
            conn.close()
            return render_template('register.html')

        # Insert the new user into the database
        cursor.execute("INSERT INTO students (name, email, password) VALUES (?, ?, ?)", (name, email, hashed_password))
        conn.commit()
        conn.close()

        # Set the session variables
        session['user_id'] = cursor.lastrowid
        session['user_type'] = 'student'

        # Redirect to the student dashboard
        return redirect(url_for('dashboard_student'))

    if 'user_id' in session:
        if session.get('user_type') == 'admin':
            return redirect(url_for('dashboard_admin'))
        elif not session.get('user_type') == 'admin':
            return redirect(url_for('dashboard_student'))
        else:
            return render_template('register.html')
    return render_template('register.html')


@app.route('/login/student', methods=['GET', 'POST'])
def login_student():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = check_user(email, password, 'student')
        if user:
            session['user_id'] = user['id']
            session['user_type'] = 'student'
            return redirect(url_for('dashboard_student'))
        else:
            flash('Invalid credentials')
    return render_template('login_student.html')

@app.route('/login/admin', methods=['GET', 'POST'])
def login_admin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = check_user(email, password, 'admin')
        if user:
            session['user_id'] = user['id']
            session['user_type'] = 'admin'
            return redirect(url_for('dashboard_admin'))
        else:
            flash('Invalid credentials')
    return render_template('login_admin.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_type', None)
    return redirect(url_for('login_student'))

@app.route('/dashboard/student')
def dashboard_student():
    if 'user_id' not in session or session.get('user_type') != 'student':
        return redirect(url_for('login_student'))
    return render_template('student_dashboard.html')

@app.route('/dashboard/admin')
def dashboard_admin():
    if 'user_id' not in session or session.get('user_type') != 'admin':
        return redirect(url_for('login_admin'))
    return render_template('dashboard.html')

@app.route('/manage_exam')
def manage_exam():
    if 'user_id' not in session or session.get('user_type') != 'admin':
        return redirect(url_for('login_admin'))
    return render_template('manage_exam.html')

@app.route('/create_exam', methods=['GET', 'POST'])
def create_exam():
    if 'user_id' not in session or session.get('user_type') != 'admin':
        return redirect(url_for('login_admin'))
    if request.method == 'POST':
        class_name = request.form['class_name']
        lecturer_name = request.form['lecturer_name']
        exam_name = request.form['exam_name']
        num_mcq = request.form['num_mcq']
        num_saq = request.form['num_saq']
        complexity = request.form['complexity']
        # Handle file upload
        files = request.files.getlist('exam_files[]')
        # Save exam details to database and handle file storage here
        return redirect(url_for('dashboard_admin'))
    return render_template('create_exam.html')

@app.route('/take_exam')
def take_exam():
    if 'user_id' not in session or session.get('user_type') != 'student':
        return redirect(url_for('login_student'))
    return render_template('take_exam.html')


@app.route('/view_results')
def view_results():
    if 'user_id' not in session or session.get('user_type') != 'student':
        return redirect(url_for('login_student'))

    conn = get_db_connection()
    cursor = conn.cursor()

    # Query to get the results
    cursor.execute('''
        SELECT e.exam_id, s.name as student_name, r.score
        FROM responses r
        JOIN student_exam_enrollments se ON r.enrollment_id = se.enrollment_id
        JOIN students s ON se.student_id = s.student_id
        JOIN exams e ON se.exam_id = e.exam_id
        WHERE s.student_id = ?
    ''', (session['user_id'],))

    results = cursor.fetchall()
    conn.close()

    return render_template('view_results.html', results=results)


@app.route('/lecturer_exams')
def lecturer_exams():
    if 'user_id' not in session or session.get('user_type') != 'admin':
        return redirect(url_for('login_admin'))

    lecturer_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT exam_id, title FROM exams WHERE lecturer_id = ?
    ''', (lecturer_id,))
    exams = cursor.fetchall()
    conn.close()

    return render_template('lecturer_exams.html', exams=exams)
@app.route('/exam_results/<int:exam_id>')
def exam_results(exam_id):
    if 'user_id' not in session or session.get('user_type') != 'admin':
        return redirect(url_for('login_admin'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT students.name AS student_name, responses.score
        FROM responses
        JOIN student_exam_enrollments ON responses.enrollment_id = student_exam_enrollments.enrollment_id
        JOIN students ON student_exam_enrollments.student_id = students.student_id
        WHERE student_exam_enrollments.exam_id = ?
    ''', (exam_id,))
    results = cursor.fetchall()
    conn.close()

    return render_template('exam_results.html', results=results)


if __name__ == '__main__':
    create_tables()
    app.run(debug=True)