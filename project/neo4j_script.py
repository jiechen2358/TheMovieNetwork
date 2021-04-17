from neo4j import GraphDatabase
#from . import neo4jdb
#from flask import current_app, _app_ctx_stack
from flask import Blueprint, render_template,session, request, jsonify
from . import mysql 

class DataStore():
    lastSearch=None

data = DataStore()

class DataFromNeo4j:

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
            nodeSet0=set()
            nodeSet1=set()
            nodesList=[]
            for i in range(length):
                record = result[i].values()
                nodeSet0.add(record[0])
                nodeSet1.add(record[1])
                linksList.append({"source":record[1], "target":record[0]})
            for node in nodeSet0:
                nodesList.append({"name":node, "label":"movie"})
            for node in nodeSet1:
                nodesList.append({"name":node, "label":"actor"})                
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
neo4jdb = DataFromNeo4j(DATABASE_URL, DATABASE_USERNAME, DATABASE_PASSWORD)


@neo4j_bp.route('/neo4jsearch', methods=['GET'])
def get_query_string():
    try:
        # fetch neo4j
        #movies = neo4jdb.get_movies(request.args["neo4jsearch"])
        #actors = neo4jdb.get_actors(request.args["neo4jsearch"])
        data.lastSearch=neo4jdb.get_moviesActorRelation(request.args["neo4jsearch"])
    finally:
        neo4jdb.close()

    return  render_template("home.html", username=session['username'])


@neo4j_bp.route("/graph")
def get_graph():
    if (data.lastSearch == None):
        '''
        graph = {
            'nodes': [{'name': 'In the Name of the Father', "group": 0},
                   {'name': 'Father of the Bride Part II', "group": 0},
                   {'name': 'Martin Short', "group": 1}, {'name': 'Steve Martin', "group": 1},
                   {'name': 'Kimberly Williams-Paisley', "group": 1}, {'name': 'Diane Keaton', "group": 1},
                   {'name': 'Philip King', "group": 1}],
            'links': [{'source': 'Diane Keaton', 'target': 'Father of the Bride Part II'},
                   {'source': 'Steve Martin', 'target': 'Father of the Bride Part II'},
                   {'source': 'Martin Short', 'target': 'Father of the Bride Part II'},
                   {'source': 'Kimberly Williams-Paisley', 'target': 'Father of the Bride Part II'},
                   {'source': 'Philip King', 'target': 'In the Name of the Father'}]
        }
        '''
        graph = {
            'nodes': [{'name': 'In the Name of the Father', "label": "movie", "year":1993, "duration":133, "description": "A man's coerced confession to an I.R.A. bombing he did not commit results in the imprisonment of his father as well. An English lawyer fights to free them.", "avgRating": 4.3},
                   {'name': 'Father of the Bride Part II', "label": "movie", "year":1995, "duration":106, "description": "George Banks must deal not only with the pregnancy of his daughter, but also with the unexpected pregnancy of his wife.", "avgRating": 3.1},
                   {'name': 'Martin Short', "label": "actor", "bio": "Martin Short was born on March 26, 1950 in Hamilton, Ontario, Canada as Martin Hayter Short. He is an actor and writer, known for Santa Clause è nei guai (2006), Vizio di forma (2014) and I tre amigos"}, 
                   {'name': 'Steve Martin', "label": "actor", "bio": "Steve Martin was born on August 14, 1945 in Waco, Texas, USA as Stephen Glenn Martin to Mary Lee (née Stewart; 1913-2002) and Glenn Vernon Martin (1914-1997), a real estate salesman and aspiring actor"},
                   {'name': 'Kimberly Williams-Paisley', "label": "actor", "bio": "Kimberly Williams-Paisley was born on September 14, 1971 in Rye, New York, USA as Kimberly Payne Williams. She is an actress and producer, known for Il padre della sposa (1991), La vita secondo Jim (2"},
                   {'name': 'Diane Keaton', "label": "actor", "bio": "Diane Keaton was born Diane Hall in Los Angeles, California, to Dorothy Deanne (Keaton), an amateur photographer, and John Newton Ignatius 'Jack' Hall, a civil engineer and real estate broker. She stu"},
                   {'name': 'Philip King', "label": "actor", "bio": "Philip King is a producer and director, known for This Is My Father (1998), Freedom Highway: Songs that Shaped a Century (2001) and Gabriel Byrne: Stories from Home (2008)"}],
            'links': [{'source': 'Diane Keaton', 'target': 'Father of the Bride Part II'},
                   {'source': 'Steve Martin', 'target': 'Father of the Bride Part II'},
                   {'source': 'Martin Short', 'target': 'Father of the Bride Part II'},
                   {'source': 'Kimberly Williams-Paisley', 'target': 'Father of the Bride Part II'},
                   {'source': 'Philip King', 'target': 'In the Name of the Father'}]
        }
        graphJson = jsonify(graph)
    else:
        graphJson=data.lastSearch
        conn = mysql.connect()
        cursor = conn.cursor()
        for node in graphJson['nodes']:
            name = node['name']
            if node['label'] == "movie":
                cursor.callproc('sp_searchmoviename', (name,))
                movieInfo = [list(map(str, row)) for row in cursor.fetchall()][0]
                node["year"] = movieInfo[0]
                node["duration"] = movieInfo[1]
                node["description"] = movieInfo[2]
                node['avgRating'] = movieInfo[3]
            elif node['label'] == "actor":
                cursor.callproc('sp_searchactorbio', (name,))
                actorBio = [list(map(str, row)) for row in cursor.fetchall()][0]
                node["bio"] = actorBio[0]+"..."
    return graphJson