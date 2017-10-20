#coding=utf-8
#Clase que gestiona el alta y actualización de verracos
from pymongo import MongoClient, errors
import tools,os
from random import randint
from urllib.parse import quote_plus

user = os.environ.get('MONGODB_USER','victor')
pwd = os.environ.get('MONGODB_PASSWORD','victor')
bd = os.environ.get('MONGODB_DATABASE','verracos')

uri = "mongodb://%s:%s@localhost:27017/%s" % (quote_plus(user), quote_plus(pwd), quote_plus(bd))
client = MongoClient(uri)

db = client.verracos
listado = db.listado

def add(verraco):

    # Validamos que la petición contiene un código de verraco
    if not 'codigo' in verraco or verraco['codigo'] == '':
        return tools.rerror('002')

    try:
        id = listado.insert_one(verraco)
        if id != '':
            r = tools.rok('001')
        else:
            r = tools.rerror('004')

    except errors.DuplicateKeyError:
        r = tools.rerror('003')

    return r


# Actualiza un verraco
# Es importante que hay que hacer actualizaciones de campos ya que, en caso contrario
# perdemos las colecciones

def update(verraco):
    codigo = {'codigo':verraco['codigo']}
    contenido = {'$set':verraco}
    db.listado.update(codigo,contenido)
    return tools.rok('006')

# Borra un verraco
def delete(codigo):
    resultado = db.listado.delete_one(codigo)
    return tools.rok('007')


# Lista todos los verracos
def list():
    return db.listado.find().sort('codigo',1)

# Recupera un verraco por listado
def find_one(id):
    return db.listado.find_one({'codigo':id})

# Inserta una imagen para un verraco
def insert_picture(id,picture):
    codigo = {'codigo':id }
    db.listado.update(codigo,{"$push": {"pictures":picture}})
    return tools.rok('002')

def delete_picture(id,picture):
    # Elimina el código de imagen del verraco
    codigo = {'codigo':id }
    db.listado.update(codigo,{"$pull": {"pictures":picture}})
    return tools.rok('003')

# Inserta un documento en la bibliografía del verraco
def insert_doc(id,doc):
    codigo = {'codigo':id }
    db.listado.update(codigo,{"$push": {"docs":doc}})
    return tools.rok('004')

# Elimina un documento de la bibliografía del verraco
def delete_doc(id,doc):
    codigo = {'codigo':id }
    r = db.listado.update(codigo,{"$pull": {"docs":doc}})
    return tools.rok('005')


# Inserta un dimensiones en las medidas del verraco
def insert_dimensions(id,doc):
    codigo = {'codigo':id }
    db.listado.update(codigo,{"$push": {"medidas":doc}})
    return tools.rok('004')

# Elimina dimensiones de las medidas del verraco
def delete_dimensions(id,doc):
    codigo = {'codigo':id }
    r = db.listado.update(codigo,{"$pull": {"medidas":doc}})
    return tools.rok('005')


# Inserta una inscripción al verraco
def insert_inscriptions(id,doc):
    codigo = {'codigo':id }
    db.listado.update(codigo,{"$push": {"inscripciones":doc}})
    return tools.rok('004')

# Elimina dimensiones de las medidas del verraco
def delete_inscriptions(id,doc):
    codigo = {'codigo':id }
    r = db.listado.update(codigo,{"$pull": {"inscripciones":doc}})
    return tools.rok('005')


def obtener_verraco_aleatorio():
    numero = str(randint(0,500)).zfill(3)
    return find_one(numero)
