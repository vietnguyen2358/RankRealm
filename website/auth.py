import re
from flask import Blueprint, flash, redirect, render_template, url_for, request
from flask_login import login_user, login_required, logout_user, current_user
from .models import User, db

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    data = request.form
    dbUser = ""
    if request.method == 'POST':
        inputEmail = request.form.get('email')
        inputPassword = request.form.get('password1')
        dbUser = User.query.filter_by(email=inputEmail).first()
        if dbUser:
            if dbUser.check_password(inputPassword):
                flash('Logged in successfully', category='success')
                login_user(dbUser, remember=True)
                return redirect(url_for('views.home'))
        else:
            flash('Invalid email or password', category='error')
    return render_template('login.html', user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        regemail = request.form.get('email')
        regusername = request.form.get('username')
        regpassword1 = request.form.get('password1')
        regpassword2 = request.form.get('password2')
        if len(regemail) < 4:
            flash('Email must be greater than 4 characters.', category='error')
        elif len(regusername) < 2:
            flash('Username must be greater than 1 character.', category='error')
        elif regpassword1 != regpassword2:
            flash('Passwords must match', category='error')
        elif len(regpassword1) < 7:
            flash('Minimum 8 characters required', category='error')
        else:
            new_user = User(
                username=regusername, 
                email=regemail
            )
            new_user.set_password(regpassword1)  # Set the password
            db.session.add(new_user)  # Add the user to the session
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))

        
    return render_template('register.html', user=current_user)


