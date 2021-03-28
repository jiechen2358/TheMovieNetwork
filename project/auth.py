from flask import Blueprint, render_template, request, url_for,session, redirect
from . import mysql 

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
	msg = ''
	if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
		# Create variables for easy access
		username = request.form['username']
		password = request.form['password']
		# Check if account exists using MySQL
		conn = mysql.connect()
		cursor = conn.cursor()
		cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password,))
		# Fetch one record and return result
		account = cursor.fetchone()
		# If account exists in accounts table in out database
		if account:
			# Create session data, we can access this data in other routes
			session['loggedin'] = True
			session['id'] = account[0]
			session['username'] = account[1]
			# Redirect to profile page 
			return redirect(url_for('main.profile'))
		else:
			# Account doesnt exist or username/password incorrect
			msg = 'Incorrect username/password!'
	return render_template('signin.html', msg = msg)


@auth.route('/signup')
def signup():
	return render_template('signup.html')

@auth.route('/logout')
def logout():
	return 'Logout'