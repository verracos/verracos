#coding=utf-8
#Clase que gestiona el alta y actualización de verracos
from pymongo import MongoClient, errors
import os
from bson.json_util import dumps
from flask import jsonify

client = MongoClient(os.environ.get('OPENSHIFT_MONGODB_DB_URL','mongodb://localhost:27017/'))
db = client.verracos
zonas = db.zonas


# Lista todos los verracos
def listado_zonas():
    return dumps(db.zonas.find({},{'zona':1,'_id':0}).sort('zona',-1))

def listado_localidades(zona):
    print dumps(db.zonas.find_one({'zona':zona},{'localidades':1,'_id':0}))
    return dumps(db.zonas.find_one({'zona':zona},{'localidades':1,'_id':0}))


