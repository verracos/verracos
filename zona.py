#coding=utf-8
#Clase que gestiona el alta y actualización de verracos
from pymongo import MongoClient, errors
import os
from bson.json_util import dumps
from urllib.parse import quote_plus

user = os.environ.get('MONGODB_USER','victor')
pwd = os.environ.get('MONGODB_PASSWORD','victor')
bd = os.environ.get('MONGODB_DATABASE','verracos')
servidor = os.environ.get('MONGODB_SERVICE_HOST','localhost')
uri = "mongodb://%s:%s@%s:27017/%s" % (quote_plus(user), quote_plus(pwd), quote_plus(servidor),quote_plus(bd))

client = MongoClient(uri)
db = client.verracos
zonas = db.zonas


# Lista todos los verracos
def listado_zonas():
    return dumps(db.zonas.find({},{'zona':1,'_id':0}).sort('zona',-1))

def listado_localidades(zona):
    return dumps(db.zonas.find_one({'zona':zona},{'localidades':1,'_id':0}))


