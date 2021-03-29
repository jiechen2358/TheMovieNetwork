from flask import Blueprint, render_template, session
from . import mysql 


main_bp = Blueprint('main_bp', __name__)


@main_bp.route('/')
def index():
	return render_template("home.html")

@main_bp.route('/profile')
def profile():
	return render_template("profile.html")