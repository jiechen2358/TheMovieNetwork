
from flask import Flask
from flaskext.mysql import MySQL
#from flask.ext.neo4jdriver import Neo4jDriver



mysql = MySQL()
#neo4jdb =Neo4jDriver()


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
	#app.config['GRAPHDB_URI'] = 'bolt://172.22.152.19:7687'
	#app.config['GRAPHDB_USER'] = 'neo4j'
	#app.config['GRAPHDB_PASS'] = 'CodeBunnyz123'
	#neo4jdb.init_app(app)

	

  	# blueprint for non-auth parts of app
	from .main import main_bp 
	app.register_blueprint(main_bp)

	# blueprint for auth routes in our app
	from .auth import auth_bp 
	app.register_blueprint(auth_bp)

	# blueprint for neo4j part of app 
	from .neo4j_script import neo4j_bp
	app.register_blueprint(neo4j_bp)

	return app