import Alternative
from json import dumps
from flask import Flask, g, Response, request, render_template
from elasticsearch import Elasticsearch
from neo4j.v1 import GraphDatabase, basic_auth

class Node(object):
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

        driver = GraphDatabase.driver('bolt://localhost', auth=basic_auth("neo4j", 'cem'))
        if not hasattr(g, 'neo4j_db'):
            db = driver.session()
        all_query="MATCH (n),(m) where n.title="+self.title+ "and m.title="+"'"+topic_name2+"'"+"CREATE (n) -[:prev]->(m) CREATE (m) -[:next]->(n)"
        print(all_query)
        results = db.run(all_query)
        return "ok"

    def addAlternative(self):
        creator="'Veli Aytekin'"
        link="'www.abc.com'"
        resource="'video'"
        driver = GraphDatabase.driver('bolt://localhost', auth=basic_auth("neo4j", 'cem'))
        if not hasattr(g, 'neo4j_db'):
            db = driver.session()
        all_query = "MATCH (n) where n.title="+self.title+"CREATE (m:alternative { creator:"+creator+", link:"+link+", resource:"+resource+"   } ) CREATE (n)-[:hasAlternative]->(m)"
        print(all_query)
        results = db.run(all_query)
        return "ok"



    def getPosition(self):
        return self.pos




def deleteNode(title):
        driver = GraphDatabase.driver('bolt://localhost', auth=basic_auth("neo4j", 'cem'))
        if not hasattr(g, 'neo4j_db'):
            db = driver.session()
        title="'"+title+"'"

        query1="match (n)- [r:hasAlternative] - (m) where n.title= "+title+ " delete r,m UNION ALL"
        query2=" match (n)- [r] - (m) where n.title="+title+" delete r,n"
        all_query=query1+ " "+query2
        print(all_query)
        results = db.run(all_query)
        es = Elasticsearch()
        es.delete_by_query(index='courses', doc_type='node',body={ 'query': { 'match': { 'title': title } } })
        return "ok"


def make_node(creator,label,link,pos,resource,title,type,tags,description):

        driver = GraphDatabase.driver('bolt://localhost', auth=basic_auth("neo4j", 'cem'))
        if not hasattr(g, 'neo4j_db'):
            db = driver.session()
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

        es = Elasticsearch()

        res = es.index(index='courses', doc_type='node', id=id,
                       body={'title': title, 'description': description, 'tags': tag_list})

        node = Node(id,creator,label,link,pos,resource,title,type,tags,description)

        if hasattr(g, 'neo4j_db'):
                g.neo4j_db.close()

        return node



