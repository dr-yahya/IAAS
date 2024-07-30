from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required
from ..models.models import Lecturer # Update with your actual user model
from . import db, bcrypt

auth_bp = Blueprint('auth', __name__, template_folder='templates')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))  # Adjust as needed

    error = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = Lecturer.query.filter_by(email=email).first()
        
        if user and bcrypt.check_password_hash(user.password_hash, password):
            login_user(user, remember=True)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.dashboard'))  # Adjust as needed
        else:
            error = 'Invalid username or password'

    return render_template('login.html', error=error)
