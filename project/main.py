from flask import Blueprint, render_template, session
from . import mysql 


main_bp = Blueprint('main_bp', __name__)


@main_bp.route('/')
def index():
	if (session.get('loggedin') == True):
		return render_template("home.html", username=session['username'])
	else: 
		return render_template("home.html")

@main_bp.route('/profile')
def profile():
	if (session.get('loggedin') == True):
		return render_template("profile.html", username= session['username'])
	else:
		return render_template('signin.html')