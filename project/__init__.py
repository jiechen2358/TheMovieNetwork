
from flask import Flask
from flaskext.mysql import MySQL



mysql = MySQL()


def create_app():
	app = Flask(__name__)
	app.secret_key = 'super secret key'

	# MySQL configurations
	app.config['MYSQL_DATABASE_USER'] = 'root'
	app.config['MYSQL_DATABASE_PASSWORD'] = 'CodeBunnyz1@'
	app.config['MYSQL_DATABASE_DB'] = 'the_movie_network'
	app.config['MYSQL_DATABASE_HOST'] = '172.22.152.19'
	mysql.init_app(app)


	# neo4j configurations
	DATABASE_USERNAME="neo4j"
	DATABASE_PASSWORD="CodeBunnyz123"
	DATABASE_URL="bolt://172.22.152.19:7687"
  

	# blueprint for auth routes in our app
	from .auth import auth as auth_blueprint
	app.register_blueprint(auth_blueprint)

	# blueprint for non-auth parts of app
	from .main import main as main_blueprint
	app.register_blueprint(main_blueprint)

	return app