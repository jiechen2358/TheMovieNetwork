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
neo4jdb = SampleDataFromNeo4j(DATABASE_URL, DATABASE_USERNAME, DATABASE_PASSWORD)


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
            'nodes': [{'name': 'In the Name of the Father', "label": "movie", "year":1993, "duration":133, "description": "George Banks must deal not only with the pregnancy of his daughter, but also with the unexpected pregnancy of his wife.", "avgRating": 4.3},
                   {'name': 'Father of the Bride Part II', "label": "movie", "year":1995, "duration":106, "description": "A man's coerced confession to an I.R.A. bombing he did not commit results in the imprisonment of his father as well. An English lawyer fights to free them.", "avgRating": 3.1},
                   {'name': 'Martin Short', "label": "actor", "bio": "Fred Astaire was born in Omaha, Nebraska, to Johanna (Geilus) and Fritz Austerlitz, a brewer. Fred entered show business at age 5. He was successful both in vaudeville and on Broadway in partnership with his sister, Adele Astaire. After Adele retired to marry in 1932, Astaire headed to Hollywood. Signed to RKO, he was loaned to MGM to appear in La danza di Venere (1933) before starting work on RKO's Carioca (1933). In the latter film, he began his highly successful partnership with Ginger Rogers, with whom he danced in 9 RKO pictures. During these years, he was also active in recording and radio. On film, Astaire later appeared opposite a number of partners through various studios. After a temporary retirement in 1945-7, during which he opened Fred Astaire Dance Studios, Astaire returned to film to star in more musicals through 1957. He subsequently performed a number of straight dramatic roles in film and TV."}, 
                   {'name': 'Steve Martin', "label": "actor", "bio": "Fred Astaire was born in Omaha, Nebraska, to Johanna (Geilus) and Fritz Austerlitz, a brewer. Fred entered show business at age 5. He was successful both in vaudeville and on Broadway in partnership with his sister, Adele Astaire. After Adele retired to marry in 1932, Astaire headed to Hollywood. Signed to RKO, he was loaned to MGM to appear in La danza di Venere (1933) before starting work on RKO's Carioca (1933). In the latter film, he began his highly successful partnership with Ginger Rogers, with whom he danced in 9 RKO pictures. During these years, he was also active in recording and radio. On film, Astaire later appeared opposite a number of partners through various studios. After a temporary retirement in 1945-7, during which he opened Fred Astaire Dance Studios, Astaire returned to film to star in more musicals through 1957. He subsequently performed a number of straight dramatic roles in film and TV."},
                   {'name': 'Kimberly Williams-Paisley', "label": "actor", "bio": "Fred Astaire was born in Omaha, Nebraska, to Johanna (Geilus) and Fritz Austerlitz, a brewer. Fred entered show business at age 5. He was successful both in vaudeville and on Broadway in partnership with his sister, Adele Astaire. After Adele retired to marry in 1932, Astaire headed to Hollywood. Signed to RKO, he was loaned to MGM to appear in La danza di Venere (1933) before starting work on RKO's Carioca (1933). In the latter film, he began his highly successful partnership with Ginger Rogers, with whom he danced in 9 RKO pictures. During these years, he was also active in recording and radio. On film, Astaire later appeared opposite a number of partners through various studios. After a temporary retirement in 1945-7, during which he opened Fred Astaire Dance Studios, Astaire returned to film to star in more musicals through 1957. He subsequently performed a number of straight dramatic roles in film and TV."}, 
                   {'name': 'Diane Keaton', "label": "actor", "bio": "Fred Astaire was born in Omaha, Nebraska, to Johanna (Geilus) and Fritz Austerlitz, a brewer. Fred entered show business at age 5. He was successful both in vaudeville and on Broadway in partnership with his sister, Adele Astaire. After Adele retired to marry in 1932, Astaire headed to Hollywood. Signed to RKO, he was loaned to MGM to appear in La danza di Venere (1933) before starting work on RKO's Carioca (1933). In the latter film, he began his highly successful partnership with Ginger Rogers, with whom he danced in 9 RKO pictures. During these years, he was also active in recording and radio. On film, Astaire later appeared opposite a number of partners through various studios. After a temporary retirement in 1945-7, during which he opened Fred Astaire Dance Studios, Astaire returned to film to star in more musicals through 1957. He subsequently performed a number of straight dramatic roles in film and TV."},
                   {'name': 'Philip King', "label": "actor", "bio": "Fred Astaire was born in Omaha, Nebraska, to Johanna (Geilus) and Fritz Austerlitz, a brewer. Fred entered show business at age 5. He was successful both in vaudeville and on Broadway in partnership with his sister, Adele Astaire. After Adele retired to marry in 1932, Astaire headed to Hollywood. Signed to RKO, he was loaned to MGM to appear in La danza di Venere (1933) before starting work on RKO's Carioca (1933). In the latter film, he began his highly successful partnership with Ginger Rogers, with whom he danced in 9 RKO pictures. During these years, he was also active in recording and radio. On film, Astaire later appeared opposite a number of partners through various studios. After a temporary retirement in 1945-7, during which he opened Fred Astaire Dance Studios, Astaire returned to film to star in more musicals through 1957. He subsequently performed a number of straight dramatic roles in film and TV."}],
            'links': [{'source': 'Diane Keaton', 'target': 'Father of the Bride Part II'},
                   {'source': 'Steve Martin', 'target': 'Father of the Bride Part II'},
                   {'source': 'Martin Short', 'target': 'Father of the Bride Part II'},
                   {'source': 'Kimberly Williams-Paisley', 'target': 'Father of the Bride Part II'},
                   {'source': 'Philip King', 'target': 'In the Name of the Father'}]
        }
        graphJson = jsonify(graph)
    else:
        graphJson=data.lastSearch
        for node in graphJson['nodes']:
            movieName = node['name']
            if node['label'] == "movie":
                #search in the movies table of mysql db, fake it for now
                node["year"] = 2000
                node["duration"] = 100
                node["description"] = "###description placeholder###"
                node['avgRating'] = 1.1
            elif node['label'] == "actor":
                #search in the actors table of mysql db, fake it for now
                node["bio"] = "****BIO placeholder****"
        print(graphJson['nodes'])
    return graphJson