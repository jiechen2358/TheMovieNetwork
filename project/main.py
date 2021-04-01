from flask import Blueprint, render_template, session, request, redirect, url_for
from . import mysql 
import json



main_bp = Blueprint('main_bp', __name__)


@main_bp.route('/')
def index():
	if (session.get('loggedin') == True):
		return render_template("home.html", username=session['username'])
	else: 
		return redirect(url_for('auth_bp.login'))

@main_bp.route('/profile')
def profile():
	if (session.get('loggedin') == True):
		return render_template("profile.html", username= session['username'])
	else:
		return redirect(url_for('auth_bp.login'))


@main_bp.route('/mysqlsearch', methods=['GET'])
def mysql_search():
	if (session.get('loggedin') == True):
		keyword = request.args["mysqlsearch"]
		conn = mysql.connect()
		cursor = conn.cursor()
		cursor.callproc('sp_mysqlsearch',(session['uid'], keyword))
		movies = [list(map(str, row)) for row in cursor.fetchall()]
		return render_template("home.html", 
			username=session['username'], uid = session['uid'], mysqlSearchResults=movies)
	else: #must login to use any search function
		return redirect(url_for('auth_bp.login'))

@main_bp.route('/rate', methods=['POST'])
def rate_movie():
	if (session.get('loggedin') == True):
		request_body = request.json
		# print(request_body)
		movieid = request_body["movielens_title_id"]
		rating = request_body['rating']
		uid = session['uid']
		conn = mysql.connect()
		cursor = conn.cursor()
		cursor.execute("INSERT INTO ratings (uid, movielens_title_id, rating) VALUES ({}, {}, {}) ON DUPLICATE KEY UPDATE rating= {};".format(uid, movieid, rating, rating))
		conn.commit()
		return "rating updated successfully :)", 200
	else: #must login to use any search function
		return redirect(url_for('auth_bp.login'))


