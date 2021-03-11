from flask import Flask, render_template, url_for
from flaskext.mysql import MySQL

app = Flask(__name__)
mysql = MySQL()

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'CodeBunnyz1@'
app.config['MYSQL_DATABASE_DB'] = 'the_movie_network'
app.config['MYSQL_DATABASE_HOST'] = '172.22.152.19'
mysql.init_app(app)

@app.route('/')
def main():
    conn = mysql.connect()
    cursor = conn.cursor()
    sql = "Select imdb_name_id, name from actors order by rand() LIMIT 10;"
    cursor.execute(sql)
    results = cursor.fetchall()
    return  render_template("home.html", results=results)

@app.route('/showSignUp')
def showSignUp():
    return render_template('signup.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0') 
