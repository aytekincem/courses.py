import Alternative
from json import dumps
from flask import Flask, g, Response, request, render_template
from elasticsearch import Elasticsearch
from neo4j.v1 import GraphDatabase, basic_auth
import courses_get

global DRIVER
global db
global es

DRIVER=courses_get.driver
db=DRIVER.session()
es = Elasticsearch()
class MyNode(object):

    id=0
    creator = ""
    label = ""
    link=""
    pos=""
    resource=""
    title=""
    type=""
    tags=[]
    description=""
    alternatives=[]
    # The class "constructor" - It's actually an initializer
    def __init__(self,id,creator,label,link,pos,resource,title,type,tags,description,alternatives=None):
        self.id=id
        self.creator = creator
        self.label = label
        self.link = link
        self.pos= pos
        self.resource = resource
        self.title = title
        self.type = type
        self.tags = tags
        self.description=description
        self.alternatives=alternatives


    def tieToTopic(self, topic_name2):

        #driver = GraphDatabase.driver('bolt://localhost', auth=basic_auth("neo4j", 'cem'))
        #if not hasattr(g, 'neo4j_db'):
            #db = driver.session()
        all_query="MATCH (n),(m) where n.title="+self.title+ "and m.title="+"'"+topic_name2+"'"+"CREATE (n) -[:prev]->(m) CREATE (m) -[:next]->(n)"
        print(all_query)
        results = db.run(all_query)
        return "ok"

    def addAlternative(self):
        creator="'Veli Aytekin'"  #becareful to the surronding '   '
        link="'www.abc.com'"
        resource="'video'"
        #driver = GraphDatabase.driver('bolt://localhost', auth=basic_auth("neo4j", 'cem'))
       # if not hasattr(g, 'neo4j_db'):
        #    db = DRIVER.session()
        all_query = "MATCH (n) where n.title="+self.title+"CREATE (m:alternative { creator:"+creator+", link:"+link+", resource:"+resource+"   } ) CREATE (n)-[:hasAlternative]->(m)"
        print(all_query)
        results = db.run(all_query)
        return "alternative added."

    def addAssesment(self):
        creator="'Ali Aytekin'"
        link="'www.xyz.com'"
        type="'multiple-choice'"
        #driver = GraphDatabase.driver('bolt://localhost', auth=basic_auth("neo4j", 'cem'))
       # if not hasattr(g, 'neo4j_db'):
            #db = DRIVER.session()
        all_query = "MATCH (n) where n.title=" + self.title + "CREATE (m:assesment { creator:" + creator + ", link:" + link + ", type:" + type + "   } ) CREATE (n)-[:hasAssesment]->(m)"
        print(all_query)
        results = db.run(all_query)
        return "assesment added."



    def getPosition(self):
        return self.pos




def deleteAlternative(title):
        #driver = GraphDatabase.driver('bolt://localhost', auth=basic_auth("neo4j", 'cem'))

       # if not hasattr(g, 'neo4j_db'):
            #db = DRIVER.session()
        title="'"+title+"'"

        query1="match (n)- [r:hasAlternative] - (m) where n.title= "+title+ " delete r,m"  # UNION ALL"
        print(query1)
        results = db.run(query1)
        return "alternative deleted"


def deleteAssesment(title):
        driver = GraphDatabase.driver('bolt://localhost', auth=basic_auth("neo4j", 'cem'))
        #if not hasattr(g, 'neo4j_db'):
           # db = driver.session()
        title = "'" + title + "'"

        query1 = "match (n)- [r:hasAssesment] - (m) where n.title= " + title + " delete r,m"  # UNION ALL"
        print(query1)
        results = db.run(query1)
        return "asessment deleted"

def deleteNode(title):
    #driver = GraphDatabase.driver('bolt://localhost', auth=basic_auth("neo4j", 'cem'))
    #if not hasattr(g, 'neo4j_db'):
        #db = DRIVER.session()

    deleteAlternative(title)
    deleteAssesment(title)

    title = "'" + title + "'"
    query1 = "match (n)- [r] - () where n.title= " + title + " delete r,n"
    print(query1)
    results = db.run(query1)
    #es = Elasticsearch()
    es.delete_by_query(index='courses', doc_type='node',body={ 'query': { 'match': { 'title': title } } })
    return "node deleted"

def make_node(creator,label,link,pos,resource,title,type,tags,description):

        #driver = GraphDatabase.driver('bolt://localhost', auth=basic_auth("neo4j", 'cem'))
        #if not hasattr(g, 'neo4j_db'):
            #db = driver.session()
        creator = "'" + creator + "'"
        label = "'" + label + "'"
        link = "'" + link + "'"
        pos = "'" + pos+ "'"
        resource = "'" + resource + "'"
        title = "'" + title + "'"
        type = "'" + type+ "'"
        description = "'" + description + "'"
        tag_list = tags
        query = " CREATE (n:course { creator :" + creator + ",label:" + label + ",link:" + link + ",pos:" + pos + ",resource:" + resource + ",title:" + title + ",type:" + type + "} ) RETURN id(n)"

        results = db.run(query)
        for record in results:
            id = record['id(n)']

        #es = Elasticsearch()

        res = es.index(index='courses', doc_type='node', id=id,
                       body={'title': title, 'description': description, 'tags': tag_list})

        node = MyNode(id,creator,label,link,pos,resource,title,type,tags,description)

        #if hasattr(g, 'neo4j_db'):
                #g.neo4j_db.close()


        return node

def getNodeInfo():
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

    #es = Elasticsearch()
    resp = es.search(index="courses", body={"query": {"match": {"_id": 1}}})
    for doc in resp['hits']['hits']:
        id = doc['_id']
        tags = doc['_source']['tags']  # tags type list.
        description = doc['_source']['description']

    print(id," ",tags," ")

    alternative_nodes = []
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

def GetLastNode():
    query="match(a:course) where not (a)-[:next]->() return a.title as title"
    results = db.run(query)
    for record in results:
        title=record['title']
    return title
