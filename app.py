#coding=utf-8
from flask import Flask, jsonify, request, redirect, url_for
from flask import render_template
import verraco, tools, os, tinys3, logging, zona
import flask.ext.login as flask_login
from user import User
from pymongo import MongoClient
from flask_mail import Mail, Message
from random import randint
from werkzeug.security import generate_password_hash
import requests
from urllib.parse import quote_plus

LOG_FILENAME = '/tmp/verracos.log'
logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG)

S3_ACCESS_KEY = os.environ.get('S3ACCESSKEY')
S3_SECRET_KEY = os.environ.get('S3SECRETKEY')
s3conn = tinys3.Connection(S3_ACCESS_KEY,S3_SECRET_KEY,'verracos',endpoint='s3-eu-west-1.amazonaws.com')

app = Flask(__name__)
app.secret_key = os.environ.get('FLASKSECRETKEY')
app.config['APPNAME'] = 'Verracos'
app.config['IMAGE_SERVER'] = 'https://s3-eu-west-1.amazonaws.com/verracos/'

# Configuracion del Login
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

# Configuracion MongoDB
user = os.environ.get('MONGODB_USER','victor')
pwd = os.environ.get('MONGODB_PASSWORD','victor')
bd = os.environ.get('MONGODB_DATABASE','verracos')
servidor = os.environ.get('MONGODB_SERVICE_HOST','localhost')
uri = "mongodb://%s:%s@%s:27017/%s" % (quote_plus(user), quote_plus(pwd), quote_plus(servidor),quote_plus(bd))
client = MongoClient(uri)

db = client.verracos
users = db.users

# Configuracion Mail
app.config['MAIL_SERVER']='mail.verracos.es'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'jose@verracos.es'
app.config['MAIL_PASSWORD'] = os.environ.get('MAILPASSWORD')
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail()
mail.init_app(app)

logging.debug('Verracos configurado')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/test')
def test():
    return 'Verracos Up & Running!!!'

@app.route('/listado')
def listado():
    verracos = verraco.list()
    return render_template('listado.html',verracos=verracos)

@app.route('/mapa')
def mapa():
    verracos = verraco.list()
    return render_template('mapa.html',verracos=verracos)

@app.route('/verraco/<id>')
def ficha(id):
    v = verraco.find_one(id)
    return render_template('ficha.html',verraco=v)

@app.route('/buscar')
def buscar():
    return render_template('buscar.html')

@app.route('/acerca-de')
def acercade():
    return render_template('acercade.html')

@app.route('/contactar', methods=['GET'])
def contactar():
    return render_template('contactar.html')

@app.route('/contactar', methods=['POST'])
def contactar_envio():

    nombre = request.form['nombre']
    email = request.form['email']
    asunto = request.form['asunto']
    comentario = request.form['comentario']

    # Mensaje a Jose

    msg = Message("Verracos: " + asunto,
                  sender=(nombre,email),
                  recipients=["jose@verracos.es"])
    msg.charset = 'UTF-8'
    msg.html = comentario
    mail.send(msg)

    # Mensaje al usuario
    msg = Message("Contacto con Verracos.es",
                  sender=("Verracos.es","jose@verracos.es"),
                  recipients=[email])
    msg.charset = 'UTF-8'
    mensaje_saludo = 'Hola ' + nombre + ',<br/><p>Gracias por contactar con Verracos.es sobre <strong>' + asunto + '</strong>. En breve recibiras una respuesta.</p><br/>Saludos, <br/><br/>Jose Cuervo'

    msg.html = mensaje_saludo
    mail.send(msg)

    return render_template('contactar_email.html',email=email)

# Devuelve un verraco aleatorio para poderlo utilizar en IFTTT
@app.route('/aleatorio', methods=['GET'])
def verraco_aleatorio():

    # Obtenemos un verraco aleatorio
    verracoaleatorio = verraco.obtener_verraco_aleatorio()

    # Recorremos todas las fotos y ponemos una aleatoria
    if 'pictures' in verracoaleatorio:
        tamanio = len(verracoaleatorio['pictures'])
        aleatorio = randint(0,tamanio-1)
        foto = 'https://s3-eu-west-1.amazonaws.com/verracos/' + verracoaleatorio['codigo'] + '/' + verracoaleatorio['pictures'][aleatorio]['file']
    else:
        foto = 'http://www.verracos.es/static/images/banner.jpg'

    # Montamos el JSON
    cadena = {'value1':verracoaleatorio['nombre'] + ' ' + verracoaleatorio['codigo'] + ' ' + verracoaleatorio['zona'],
              'value2': foto,
              'value3':'http://www.verracos.es/verraco/' + verracoaleatorio['codigo'],
              }

    # Llamamos al webhook
    requests.post('https://maker.ifttt.com/trigger/verraco/with/key/PDTE5', json = cadena)

    #Retornamos el JSON con el verraco
    return jsonify(cadena)



# ADMIN

@app.route('/admin/')
@flask_login.login_required
def admin():
    verracos = verraco.list()
    return render_template('admin/list.html',verracos=verracos)

@app.route('/admin/add')
@flask_login.login_required
def admin_add():
    return render_template('admin/add.html')

@app.route('/admin/update/<id>')
@flask_login.login_required
def admin_update(id):
    v = verraco.find_one(id)
    return render_template('admin/update.html',verraco=v)

@app.route('/admin/delete/<id>')
@flask_login.login_required
def admin_delete():
    return render_template('add.html')

@app.route('/admin/picture/<id>')
@flask_login.login_required
def admin_picture(id):
    # PENDIENTE: Hay que comprobar que el verraco existe, si no sacar pantalla de error
    v = verraco.find_one(id)
    return render_template('admin/picture.html',id=id, verraco=v)

@app.route('/admin/doc/<id>')
@flask_login.login_required
def admin_doc(id):
    # PENDIENTE: Hay que comprobar que el verraco existe, si no sacar pantalla de error
    v = verraco.find_one(id)
    return render_template('admin/doc.html',id=id, verraco=v)


@app.route('/admin/dimensions/<id>')
@flask_login.login_required
def admin_dimensions(id):
    # PENDIENTE: Hay que comprobar que el verraco existe, si no sacar pantalla de error
    v = verraco.find_one(id)
    return render_template('admin/dimensions.html',id=id, verraco=v)


# Administración de Inscripciones
@app.route('/admin/inscript/<id>')
@flask_login.login_required
def admin_inscriptions(id):
    # PENDIENTE: Hay que comprobar que el verraco existe, si no sacar pantalla de error
    v = verraco.find_one(id)
    return render_template('admin/inscript.html',id=id, verraco=v)


# API

@app.route('/api/verraco', methods=['POST'])
def api_add():

    # Con force=True obtenemos la peticion aunque no sea app/json
    peticion = request.get_json()
    #or not 'codigo' in request.json
    #if not request.json:
    #    return jsonify({'resultado':tools.rerror('001')})

    resultado = verraco.add(peticion)
    return jsonify({'resultado':resultado})


@app.route('/api/verraco', methods=['PUT'])
def api_update():

    peticion = request.get_json()
    resultado = verraco.update(peticion)
    return jsonify({'resultado':resultado})


@app.route('/api/verraco', methods=['DELETE'])
def api_delete():
    # Borramos todo el verraco

    peticion = request.get_json()

    # Borramos todas las imágenes de S3 borrando el directorio
    # Borramos los ficheros del directorio uno a uno y luego el directorio
    lista = s3conn.list(peticion['codigo'],'verracos')

    for fichero in lista:
        s3conn.delete(fichero['key'])
    # Borramos el directorio
    s3conn.delete(peticion['codigo']+'/')

    resultado = verraco.delete(peticion)
    return jsonify({'resultado':resultado})

@app.route('/api/verraco/<id>/picture', methods=['POST'])
def api_picture_add(id):

    # Recibe un contenido multipart con la fotografía y la fecha y autor
    # En este caso no es JSON

    autor = request.values['autor']
    fecha = request.values['fecha']
    files = request.files['fotografia']

    if files:
        filename = files.filename
        dir = os.environ.get('OPENSHIFT_TMP_DIR','/tmp')
        files.save(os.path.join(dir, filename))
        f = open(os.path.join(dir, filename),'rb')

        # Subimos el fichero a s3
        s3conn.upload(id+'/'+filename,f,'verracos')

        # Creamos el json e insertamos imágen
        picture = {
            'file': filename,
            'autor': autor,
            'fecha': fecha
        }

        # Insertamos imagen en DB
        resultado = verraco.insert_picture(id,picture)

    else:
        resultado = tools.rerror('005')

    return jsonify({'resultado':resultado})


@app.route('/api/verraco/<id>/picture/<filename>', methods=['DELETE'])
def api_picture_delete(id,filename):
    # Borra una imagen
    # En la URL va tanto el id del verraco como el id de la imagen
    # Las imagenes se componen del código del verraco y el nombre del fichero

    # Borramos la imagen de S3
    s3conn.delete(id+'/'+filename,'verracos')

    # Si se ha borrado de S3 entonces la borramos de MongDB
    picture = {
            'file': filename,
    }

    resultado = verraco.delete_picture(id,picture)
    return jsonify({'resultado':resultado})


@app.route('/api/verraco/<id>/doc', methods=['POST'])
def api_doc_add(id):
    # Inserta un documento a la bibliografía del Verraco
    # Con force=True obtenemos la peticion aunque no sea app/json
    peticion = request.get_json()
    resultado = verraco.insert_doc(id,peticion)
    return jsonify({'resultado':resultado})

@app.route('/api/verraco/<id>/doc/<iddoc>', methods=['DELETE'])
def api_doc_delete(id,iddoc):
    # Elimina un documento de la bibliografía del verraco

    doc = {
            'codigo': long(iddoc),
    }

    resultado = verraco.delete_doc(id,doc)
    return jsonify({'resultado':resultado})


# API para las dimensiones del verraco
@app.route('/api/verraco/<id>/dimensions', methods=['POST'])
def api_dimensions_add(id):
    # Inserta un dimensiones en el Verraco
    # Con force=True obtenemos la peticion aunque no sea app/json
    peticion = request.get_json()
    resultado = verraco.insert_dimensions(id,peticion)
    return jsonify({'resultado':resultado})

@app.route('/api/verraco/<id>/dimensions/<iddoc>', methods=['DELETE'])
def api_dimensions_delete(id,iddoc):
    # Elimina unas dimensiones del verraco de su listado de dimensiones

    doc = {
            'codigo': long(iddoc),
    }

    resultado = verraco.delete_dimensions(id,doc)
    return jsonify({'resultado':resultado})



# API para las inscripciones del verraco
@app.route('/api/verraco/<id>/inscriptions', methods=['POST'])
def api_inscriptions_add(id):
    # Inserta una inscripción en el Verraco
    # Con force=True obtenemos la peticion aunque no sea app/json
    peticion = request.get_json()
    resultado = verraco.insert_inscriptions(id,peticion)
    return jsonify({'resultado':resultado})

@app.route('/api/verraco/<id>/inscriptions/<iddoc>', methods=['DELETE'])
def api_inscriptions_delete(id,iddoc):
    # Elimina una de las inscripciones del verraco de su listado de inscripciones

    doc = {
            'codigo': long(iddoc),
    }

    resultado = verraco.delete_inscriptions(id,doc)
    return jsonify({'resultado':resultado})

@app.route('/api/zona', methods=['GET'])
def api_zona():
    # Devolvemos todas las zonas que existan
    resultado = zona.listado_zonas()
    return resultado

@app.route('/api/zona/<idzona>', methods=['GET'])
def api_localidades(idzona):
    # Devolvemos todas las zonas que existan
    resultado = zona.listado_localidades(idzona)
    return resultado

# Login

@login_manager.user_loader
def user_loader(user_id):
    usuario = users.find_one({"_id": user_id})
    if not usuario:
        return None
    return User(usuario['_id'])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login/login.html')

    # Cargamos el usuario de la BD
    usuario = users.find_one(request.form['username'])

    # Comprobamos los passwords
    if usuario and User.validate_login(usuario['password'],request.form['password']):
        # Creamos un objeto usuario
        user = User(usuario['_id'])
        #login del objeto user
        flask_login.login_user(user)
        return redirect(url_for('admin'))

    return render_template('login/login.html',error=True)


@app.route('/logout')
def logout():
    flask_login.logout_user()
    return render_template('login/logout.html')

@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('login/unauthorized.html')


def on_json_loading_failed():
    logging.debug('callback')

if __name__ == '__main__':
    logging.debug('Arrancando aplicación Verracos')
    app.run(host='0.0.0.0', port='8080')
