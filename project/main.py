from flask import Blueprint, render_template,session
from . import mysql 


main = Blueprint('main', __name__)


@main.route('/')
def index():
	return render_template("home.html")

@main.route('/profile')
def profile():
	return 'hi {}, here is your profile'.format(session['username'])