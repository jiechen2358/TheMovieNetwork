from flask import Blueprint, render_template, session, request, redirect, url_for
from . import mysql 
import json



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


@main_bp.route('/mysqlsearch', methods=['GET'])
def mysql_search():
	keyword = request.args["mysqlsearch"]
	conn = mysql.connect()
	cursor = conn.cursor()
	cursor.execute("SELECT * FROM movies WHERE title LIKE '%{}%'".format(keyword)) 
	movies = [list(map(str, row)) for row in cursor.fetchall()]
	# badly written, maybe redirect to .index with added argument mysqlSearchResults
	if (session.get('loggedin') == True):
		session['mysqlSearchResults'] = movies
		return render_template("home.html", username=session['username'], mysqlSearchResults=movies)
	else: 
		return render_template("home.html", mysqlSearchResults=movies)


