import re
from flask import Blueprint, flash, redirect, render_template, url_for, request

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    data = request.form
    return render_template('login.html')

@auth.route('/logout')
def logout():
    return redirect(url_for('auth.login'))

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

    if len(email) < 4:
        flash('Email must be greater than 4 characters.', category='error')
    elif len(username) < 2:
            flash('Username must be greater than 1 character.', category='error')
    elif password1 != password2:
        flash('Passwords must match', category='error')
    elif len(password1) < 7:
        flash('Minimum 8 characters required', category='error')
    else:
        flash('Account created!', category='success')
        
    return render_template('register.html')


