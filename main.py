from flask import Flask, render_template, url_for, request, json
from flaskext.mysql import MySQL
from neo4j import GraphDatabase
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
mysql = MySQL()

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

class SampleDataFromNeo4j:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def read_sample_from_neo4j(self):
        with self.driver.session() as session:
            movies = session.read_transaction(self._read_movie_neo4j)
            actors = session.read_transaction(self._read_actor_neo4j)
            return_result = []
            for i in range(len(movies)):
                return_result.append([movies[i], actors[i]])
            return return_result
    
    @staticmethod
    def _read_movie_neo4j(tx):
        result = tx.run("MATCH (n:Movie) RETURN n LIMIT 3")
        return_data = []
        for record in result:        
            return_data.append(record.values())
        return return_data

    @staticmethod
    def _read_actor_neo4j(tx):
        result = tx.run("MATCH (n:Actors) RETURN n LIMIT 3")
        return_data = []
        for record in result:
            return_data.append(record.values())
        return return_data

    @staticmethod
    def _read_relation_neo4j(tx):
        result = tx.run("MATCH p=()-[r:Cast]->() RETURN p LIMIT 2")
        return_data = []
        for record in result:
            return_data.append(record.values())
        print(return_data)
        return return_data

@app.route('/')
def main():
    try:
        # fetch from mysql
        conn = mysql.connect()
        cursor = conn.cursor()
        sql = "Select imdb_name_id, name from actors order by rand() LIMIT 10;"
        cursor.execute(sql)
        results = cursor.fetchall()

    finally:
        cursor.close()
        conn.close()
    
    try:
        # fetch neo4j
        neo4jdb = SampleDataFromNeo4j(DATABASE_URL, DATABASE_USERNAME, DATABASE_PASSWORD)
        movies_actors = neo4jdb.read_sample_from_neo4j()

    finally:
        neo4jdb.close()
    
    return  render_template("home.html", results=results, neo4jResults=movies_actors)
        

@app.route('/showSignIn')
def showSignIn():
    return render_template('signin.html')

@app.route('/showSignUp')
def showSignUp():
    return render_template('signup.html')

@app.route('/signUp', methods=['POST'])
def signUp():
    # read the posted values from the UI
    _username = request.form['username']
    _password = request.form['password']
    # validate the received values
    if _username and _password:
        try:
            # All Good, let's call MySQL            
            conn = mysql.connect()
            cursor = conn.cursor()
            _hashed_password = generate_password_hash(_password, method="sha1")
            cursor.callproc('sp_createUser',(_username,_hashed_password))
            data = cursor.fetchall()

            if len(data) is 0:
                conn.commit()
                return json.dumps({'message':'User created successfully !'})
            else:
                return json.dumps({'error':str(data[0])})
        finally:
            cursor.close()
            conn.close()

    else:
        return json.dumps({'html':'<span>Enter the required fields</span>'})

if __name__ == '__main__':
    app.run(host='0.0.0.0',port='5001') 
