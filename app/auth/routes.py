from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from app.models.bicycle import User
from app.extensions import db
from sqlalchemy.exc import IntegrityError

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('main.home'))

        flash('Email or Password are incorrect!', 'danger')

    return render_template('auth/login.html')

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Passwords are not similarly!', 'danger')
            return redirect(url_for('auth.signup'))

        # Checking for unique email
        if User.query.filter(User.email == email).first():
            flash('User with this email already existing!', 'danger')
            return redirect(url_for('auth.signup'))

        # Creating new user
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        try:
            db.session.commit()
            flash('Registration was successful! Now you can log in!', 'success')
        except IntegrityError:
            db.session.rollback()
            flash('Database error! User with this email may exist!', 'danger')
            return redirect(url_for('auth.signup'))

        return redirect(url_for('auth.login'))

    return render_template('auth/signup.html')


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.home'))
