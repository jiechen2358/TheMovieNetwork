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
		conn = mysql.connect()
		cursor = conn.cursor()
		cursor.callproc('sp_profile',(session['uid'],))
		movies = [list(map(str, row)) for row in cursor.fetchall()]
		return render_template("profile.html", username= session['username'],
			uid = session['uid'], ratedMovies=movies)
	else:
		return redirect(url_for('auth_bp.login'))


@main_bp.route('/mysqlsearch', methods=['GET','POST'])
def mysql_search():
	if (session.get('loggedin') == True):
		keyword = request.form.get("Keywords")
		minrating = request.form.get("Rating")
		genre = request.form.get("Genres")
		conn = mysql.connect()
		cursor = conn.cursor()
		movies = []
		if (genre == ''):
			cursor.callproc('sp_mysqlsearch',(session['uid'], keyword, minrating))
			movies = [list(map(str, row)) for row in cursor.fetchall()]
		else:
			cursor.callproc('sp_mysqlsearchWithGenre',(session['uid'], keyword, minrating,genre))
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

@main_bp.route('/delete_rating', methods=['POST'])
def delete_rating():
	if (session.get('loggedin') == True):
		request_body = request.json		
		print(request_body)
		conn = mysql.connect()
		cursor = conn.cursor()
		cursor.execute("DELETE FROM ratings WHERE movielens_title_id={} AND uid={}".format(request_body["movielens_title_id"],session['uid']))
		conn.commit()
		return "rating deleted successfully :)", 200
	else: #must login to use any search function
		return redirect(url_for('auth_bp.login'))


