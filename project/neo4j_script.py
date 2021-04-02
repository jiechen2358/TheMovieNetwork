from neo4j import GraphDatabase
#from . import neo4jdb
#from flask import current_app, _app_ctx_stack
from flask import Blueprint, render_template,session, request, jsonify


class DataStore():
    lastSearch=None

data = DataStore()

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

    def get_moviesNodesOnly(self, q):
        with self.driver.session() as session:
            result = session.read_transaction(lambda tx: list(tx.run("MATCH (movie:Movie) "
                                                             "WHERE movie.movieTitle =~ $title "
                                                             "RETURN {nodes: collect(movie.movieTitle)[..5]} AS result", {"title": "(?i).*" + q + ".*"}
                                                             )))
            graphJson=result[0].values()[0]
            nodesList=graphJson["nodes"]
            length = len(nodesList)
            nodesNewList = []
            linksList=[]
            for i in range(length):
                nodesNewList.append({"name":nodesList[i]})
                linksList.append({"source": nodesList[i], "target": nodesList[0]})
            graphJson["links"] = linksList
            graphJson['nodes'] = nodesNewList
            return graphJson


    def get_moviesActorRelation(self, q):
        with self.driver.session() as session:
            result = session.read_transaction(lambda tx: list(tx.run("MATCH p=(movie:Movie)-[r:Cast]->(actor:Actors) "
                                                            "WHERE movie.movieTitle=~ $title or actor.actor_name=~ $title "
                                                            "RETURN movie.movieTitle as target, actor.actor_name as source LIMIT 10",
                                                            {"title": "(?i).*" + q + ".*"}
                                                            )))
            graphJson={}
            length = len(result)
            linksList=[]
            nodeSet=set()
            nodesList=[]
            for i in range(length):
                record = result[i].values()
                nodeSet.add(record[0])
                nodeSet.add(record[1])
                linksList.append({"source":record[1], "target":record[0]})
            for node in nodeSet:
                nodesList.append({"name":node})
            graphJson["links"] = linksList
            graphJson['nodes'] = nodesList
            return graphJson

    def get_actors(self, q):
        with self.driver.session() as session:
            actors = []
            result = session.read_transaction(lambda tx: list(tx.run("MATCH (actor:Actors) "
                                                             "WHERE actor.actor_name =~ $name "
                                                             "RETURN actor", {"name": "(?i).*" + q + ".*"}
                                                             )))
            for record in result:
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
        #data.lastSearch = neo4jdb.get_moviesNodesOnly(request.args["neo4jsearch"])
        data.lastSearch=neo4jdb.get_moviesActorRelation(request.args["neo4jsearch"])
    finally:
        neo4jdb.close()

    return  render_template("home.html", neo4jSearchMovieResults=movies, neo4jSearchActorResults=actors)


@neo4j_bp.route("/graph")
def get_graph():
    if (data.lastSearch == None):
        graph = {
            "nodes": [{"name": "Titanic"}, {"name": "Kate Winslet"},
                      {"name": "Inception"}, {"name": "Leonardo Dicaprio"},
                      {"name": "James Cameron"}],
            "links": [{"source": "Kate Winslet", "target": "Titanic"},
                      {"source": "James Cameron", "target": "Titanic"},
                      {"source": "Leonardo Dicaprio", "target": "Titanic"},
                      {"source": "Leonardo Dicaprio", "target": "Inception"},
                      {"source": "Kate Winslet", "target": "Inception"}]
        }
        graphJson = jsonify(graph)
    else:
        graphJson=data.lastSearch

    return graphJson