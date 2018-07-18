#!/usr/bin/env python
import os
import MyNode
import Alternative
from json import dumps
from flask import Flask, g, Response, request, render_template
from elasticsearch import Elasticsearch
from flask_cors import CORS
from neo4j.v1 import GraphDatabase, basic_auth
from py2neo import Graph,Node,Relationship
app = Flask(__name__, static_url_path='/static/') #main web app objemiz.
CORS(app)   #for cross domain.
#password = os.getenv("NEO4J_PASSWORD")
#change2

global driver
driver = GraphDatabase.driver('bolt://localhost', auth=basic_auth("neo4j", 'cem'),encrypted=False,keep_alive=True)

global es
es=Elasticsearch()
def getNext(current_topic):
    db = get_db()
    query="MATCH (n:course)-[:next]->(next_course) WHERE n.title='"+current_topic+"' RETURN collect(next_course.title) as returned_course "
    print(query)
    results = db.run(query)

    nodes = []

    for record in results:

        for name in record['returned_course']:  #name string
            courses = {"title": name}  # dictionary objesi yarat.

            nodes.append(courses)


    return Response(dumps({"nodes": nodes, }),
                mimetype="application/json")

def getPrev(current_topic):
    db = get_db()
    query="MATCH (n:course)-[:prev]->(prev_course) WHERE n.title='"+current_topic+"' RETURN collect(prev_course.title) as returned_course "
    print(query)
    results = db.run(query)

    nodes = []

    for record in results:

        for name in record['returned_course']:  #name string
            courses = {"title": name}  # dictionary objesi yarat.

            nodes.append(courses)


    return Response(dumps({"nodes": nodes, }),
                mimetype="application/json")

def DoElasticSearch(id):
        es = Elasticsearch()
        resp = es.search(index="courses", body={"query": {"match": {"_id": id}}})
        for doc in resp['hits']['hits']:
            id = doc['_id']
            tags = doc['_source']['tags']  # tags type list.
            description = doc['_source']['description']
        return Response(dumps({"tags": tags, "description": description}),
                        mimetype="application/json")

def get_db():
    if not hasattr(g, 'neo4j_db'):
        g.neo4j_db = driver.session()
    return g.neo4j_db

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'neo4j_db'):
        g.neo4j_db.close()

@app.route("/")

def get_index():

    return app.send_static_file('index.html')

@app.route("/elasticsearch",methods=['GET','POST'])

def giveData():

    req_data = request.get_json()  # turn it into python format from json.

    topic_id = req_data['id']

    if request.method == 'POST':

        return DoElasticSearch(topic_id)

@app.route("/getNode",methods=['GET','POST'])

def getNode():

    return MyNode.getNodeInfo()

@app.route("/getPrev",methods=['GET','POST'])

def getPrevious():
    i=100
    liste=[]
    while(i>0):
        i=i-1
        getPrev("C")
        liste.append("x")

    return "OK"

@app.route("/makeNode",methods=['GET','POST'])
def makeNode():
    lastNode=""
    lastNode = MyNode.GetLastNode()
    node=MyNode.make_node("Ali", "CS300", "www.yahoo.com", "mid", "video", "D", "topic", ["a", "b", "c"], "This is course D")
    node.tieToTopic(lastNode)
    node.addAlternative()
    node.addAssesment()

    return "ok"



@app.route("/deleteNode",methods=['GET','POST'])
def deleteNode():
    MyNode.deleteNode("D")
    return "ok"


@app.route("/graph")
def get_graph():
    db = get_db()
    results = db.run("MATCH (n:course) RETURN n.label as label, n.title as title ")
    nodes = []
    for record in results:
        nodes.append(   {"title": record["title"] , "label":  record["label"]      }   )
    return Response(dumps( {"nodes": nodes } ),
                    mimetype="application/json")

@app.route('/json-exchange', methods=['GET','POST']) #GET requests will be blocked


def json_example():
    #req_data = request.get_json()   #turn it into python format from json.

    current_topic = request.form['topic']


    if request.method == 'POST':
       return getNext(current_topic)


if __name__ == '__main__':
    app.run(port=8080,host='0.0.0.0',debug=True)
