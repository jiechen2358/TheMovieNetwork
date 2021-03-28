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
		# Check if user exists using MySQL
		conn = mysql.connect()
		cursor = conn.cursor()
		cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password,))
		# Fetch one record and return result
		user = cursor.fetchone()
		# If user exists in our database
		if user:
			# Create session data, we can access this data in other routes
			session['loggedin'] = True
			session['id'] = user[0]
			session['username'] = user[1]
			# Redirect to profile page 
			return redirect(url_for('main.profile'))
		else:
			# User doesnt exist or username/password incorrect
			msg = 'Incorrect username/password!'
	return render_template('signin.html', msg = msg)

def try_create_user(username, password):
	conn = mysql.connect()
	cursor = conn.cursor()
	cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
	user = cursor.fetchone()
	if user:
		return 'User already exists!'
	else:
		cursor.execute('INSERT INTO users VALUES (NULL, %s, %s)', (username, password,))
		conn.commit()
		return 'You have successfully registered!'

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
	# Output message if something goes wrong...
	msg = ''
	# Check if "username", "password" POST requests exist (user submitted form)
	if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
		# Create variables for easy access
		username = request.form['username']
		password = request.form['password']
		msg = try_create_user(username,password)
		

	elif request.method == 'POST':
		# Form is empty... (no POST data)
		msg = 'Please fill out the form!'
	# Show registration form with message (if any)
	return render_template('signup.html', msg=msg)

@auth.route('/logout')
def logout():
	# Remove session data, this will log the user out
	session.pop('loggedin', None)
	session.pop('id', None)
	session.pop('username', None)
	return redirect(url_for('login'))
