from neo4j import GraphDatabase
#from . import neo4jdb
#from flask import current_app, _app_ctx_stack
from flask import Blueprint, render_template,session, request, jsonify
from . import mysql 

class DataStore():
    lastSearch=None
    dbClkSearch=None

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
                                                            "RETURN movie.movieId,actor.actor_id LIMIT 10",
                                                            {"title": "(?i).*" + q + ".*"}
                                                            )))
            return result

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
        data.dbClkSearch=None
    finally:
        neo4jdb.close()
    return  render_template("home.html", username=session['username'])

@neo4j_bp.route('/neo4jDbclickSearch', methods=['GET'])
def get_query_string_dbClick():
    try:
        # fetch neo4j
        data.dbClkSearch=neo4jdb.get_moviesActorRelation(request.args["neo4jDbclickSearch"])
    finally:
        neo4jdb.close()
    return  render_template("home.html", username=session['username'])

@neo4j_bp.route("/graph")
def get_graph():
    if (data.lastSearch == None and data.dbClkSearch==None):
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
            'nodes': [{"name":'tt0107207','title': 'In the Name of the Father', "label": "movie", "year":1993, "duration":133, "description": "A man's coerced confession to an I.R.A. bombing he did not commit results in the imprisonment of his father as well. An English lawyer fights to free them.", "avgRating": 4.3},
                   {"name":'tt0113041','title': 'Father of the Bride Part II', "label": "movie", "year":1995, "duration":106, "description": "George Banks must deal not only with the pregnancy of his daughter, but also with the unexpected pregnancy of his wife.", "avgRating": 3.1},
                   {"name":"nm0001737",'title': 'Martin Short', "label": "actor", "bio": "Martin Short was born on March 26, 1950 in Hamilton, Ontario, Canada as Martin Hayter Short. He is an actor and writer, known for Santa Clause è nei guai (2006), Vizio di forma (2014) and I tre amigos"}, 
                   {"name":"nm0000188",'title': 'Steve Martin', "label": "actor", "bio": "Steve Martin was born on August 14, 1945 in Waco, Texas, USA as Stephen Glenn Martin to Mary Lee (née Stewart; 1913-2002) and Glenn Vernon Martin (1914-1997), a real estate salesman and aspiring actor"},
                   {"name":"nm0931090",'title': 'Kimberly Williams-Paisley', "label": "actor", "bio": "Kimberly Williams-Paisley was born on September 14, 1971 in Rye, New York, USA as Kimberly Payne Williams. She is an actress and producer, known for Il padre della sposa (1991), La vita secondo Jim (2"},
                   {"name":"nm0000473",'title': 'Diane Keaton', "label": "actor", "bio": "Diane Keaton was born Diane Hall in Los Angeles, California, to Dorothy Deanne (Keaton), an amateur photographer, and John Newton Ignatius 'Jack' Hall, a civil engineer and real estate broker. She stu"},
                   {"name":"nm2535022",'title': 'Philip King', "label": "actor", "bio": "Philip King is a producer and director, known for This Is My Father (1998), Freedom Highway: Songs that Shaped a Century (2001) and Gabriel Byrne: Stories from Home (2008)"}],
            'links': [{'source': 'nm0000473', 'target': 'tt0113041'},
                   {'source': 'nm0000188', 'target': 'tt0113041'},
                   {'source': 'nm0001737', 'target': 'tt0113041'},
                   {'source': 'nm0931090', 'target': 'tt0113041'},
                   {'source': 'nm2535022', 'target': 'tt0107207'}]
        }
        graphJson = jsonify(graph)
    elif (data.lastSearch == None and data.dbClkSearch!=None):
        neo4jResults=data.dbClkSearch
        data.lastSearch = neo4jResults
        graphJson=convertResultToGraph(neo4jResults)
    elif (data.lastSearch != None and data.dbClkSearch==None):
        neo4jResults=data.lastSearch
        graphJson=convertResultToGraph(neo4jResults)
    elif (data.lastSearch != None and data.dbClkSearch!=None):
        neo4jOldResults=data.lastSearch
        neo4jNewResults=data.dbClkSearch
        neo4jResults=mergeDistinctData(neo4jOldResults, neo4jNewResults)
        data.lastSearch = neo4jResults
        graphJson=convertResultToGraph(neo4jResults)
    return graphJson

def mergeDistinctData(list1, list2):
    resultSet = set()
    for item in list1:
        resultSet.add(item)
    for item in list2:
        resultSet.add(item)
    return resultSet

def convertResultToGraph(neo4jResults):
    movieNodeSet=set()
    actorNodeSet=set()
    linksList=[]
    nodesList=[]
    graphJson={}
    conn = mysql.connect()
    cursor = conn.cursor()

    for neo4jResult in neo4jResults:
        record = neo4jResult.values()
        movieNodeSet.add(record[0])
        actorNodeSet.add(record[1])
        linksList.append({"source":record[1], "target":record[0]})

    movieNodeList = list(movieNodeSet)
    actorNodeList = list(actorNodeSet)

    s = "\',\'"
    movieIds = "\'" + s.join(movieNodeList) + "\'"
    actorIds = "\'" + s.join(actorNodeList) + "\'"

    cursor.callproc('sp_searchmoviebyidarray', (movieIds,))
    movieInfos = [list(map(str, row)) for row in cursor.fetchall()]
    for movieInfo in movieInfos:
        nodesList.append({"name":movieInfo[0], "title":movieInfo[1], "year":movieInfo[2],"duration":movieInfo[3],"description":movieInfo[4],'avgRating':movieInfo[5],"label":"movie"})

    cursor.callproc('sp_searchactorbyidarray', (actorIds,))
    actorInfos = [list(map(str, row)) for row in cursor.fetchall()]
    for actorInfo in actorInfos:
        nodesList.append({"name":actorInfo[0], "title":actorInfo[1], "bio":actorInfo[2]+'...',"label":"actor"})
    graphJson["links"] = linksList
    graphJson['nodes'] = nodesList
    return graphJson