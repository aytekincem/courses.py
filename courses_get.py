#!/usr/bin/env python
import os
import Node
import Alternative
from json import dumps
from flask import Flask, g, Response, request, render_template
from elasticsearch import Elasticsearch
from flask_cors import CORS
from neo4j.v1 import GraphDatabase, basic_auth

app = Flask(__name__, static_url_path='/static/') #main web app objemiz.
CORS(app)   #for cross domain.
#password = os.getenv("NEO4J_PASSWORD")
#change2

driver = GraphDatabase.driver('bolt://localhost',auth=basic_auth("neo4j", 'cem'))


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

def getNodeInfo():
    db = get_db()
    results = db.run("MATCH (n:course) where id(n)=1 RETURN n.label as label, n.title as title , n.creator as creator , n.link as link , n.pos as pos, n.resource as resource, n.type as type ")
    nodes = []
    for record in results:
        label=record['label']
        title=record['title']
        creator = record['creator']
        link= record['link']
        pos= record['pos']
        resource = record['resource']
        type = record['type']

    print(label," ",title," ",creator)

    es = Elasticsearch()
    resp = es.search(index="courses", body={"query": {"match": {"_id": 1}}})
    for doc in resp['hits']['hits']:
        id = doc['_id']
        tags = doc['_source']['tags']  # tags type list.
        description = doc['_source']['description']

    print(id," ",tags," ")

    alternative_nodes = []

    db = get_db()
    query = "MATCH (n:course)-[:hasAlternative]->(alternative) WHERE id(n)=1 RETURN alternative.creator as al_creator,id(alternative) as al_id, alternative.link as al_link, alternative.resource as al_resource "
    results = db.run(query)
    for record in results:
        al_id=record['al_id']
        al_creator = record['al_creator']
        al_link = record['al_link']
        al_resource = record['al_resource']
        alternative_node=Alternative.make_alternative(al_id,al_creator,al_link,al_resource)
        alternative_nodes.append(alternative_node)
    print(al_creator)

    return "ok"

@app.route("/makeNode",methods=['GET','POST'])
def makeNode():
    node=Node.make_node("Eralp","CS300","www.yahoo.com","mid","video","B","topic",["a","b","c"],"This is course B")
    if(node.getPosition()!="start"):
        node.tieToTopic("A")
    node.addAlternative()
    node.addAssesment()

    #node.addAlternative()

    return "ok"

@app.route("/deleteNode",methods=['GET','POST'])
def deleteNode():
    Node.deleteNode("B")
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
