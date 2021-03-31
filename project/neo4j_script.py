from neo4j import GraphDatabase
#from . import neo4jdb
#from flask import current_app, _app_ctx_stack
from flask import Blueprint, render_template,session, request


class SampleDataFromNeo4j:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def get_movies(self, q):
        with self.driver.session() as session:
            movies = []
            result = session.read_transaction(lambda tx: list(tx.run("MATCH (movie:Movie) "
                                                             "WHERE movie.movieTitle =~ $title "
                                                             "RETURN movie", {"title": "(?i).*" + q + ".*"}
                                                             )))
            for record in result:
                movies.append(record.values())
            return movies

    def get_actors(self, q):
        with self.driver.session() as session:
            actors = []
            result = session.read_transaction(lambda tx: list(tx.run("MATCH (actor:Actors) "
                                                             "WHERE actor.actor_name =~ $name "
                                                             "RETURN actor", {"name": "(?i).*" + q + ".*"}
                                                             )))
            print(result)
            for record in result:
                print(record)
                actors.append(record.values())
            return actors

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
    
    

neo4j_bp = Blueprint('neo4j_bp', __name__)

# neo4j configurations
DATABASE_USERNAME="neo4j"
DATABASE_PASSWORD="CodeBunnyz123"
DATABASE_URL="bolt://172.22.152.19:7687"
neo4jdb = SampleDataFromNeo4j(DATABASE_URL, DATABASE_USERNAME, DATABASE_PASSWORD)


@neo4j_bp.route('/neo4jsearch', methods=['GET'])
def get_query_string():
    try:
        # fetch neo4j
        movies = neo4jdb.get_movies(request.args["neo4jsearch"])
        actors = neo4jdb.get_actors(request.args["neo4jsearch"])
    finally:
        neo4jdb.close()

    return  render_template("home.html", neo4jSearchResults=[movies,actors])

    
