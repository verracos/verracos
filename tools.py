#coding=utf-8

errores = {'001':'JSON Mal definido',
           '002':'Falta código del verraco',
           '003':'Clave duplicada. El verraco ya está catalogado',
           '004':'Error insertando en base de datos',
           '005':'Error subiendo el fichero'
           }


oks = {'001':'Verraco insertado correctamente',
       '002':'Foto insertada correctamente',
       '003':'Foto eliminada correctamente',
       '004':'Documento insertado correctamente',
       '005':'Documento eliminado correctamente',
       '006':'Verraco actualizado correctamente',
       '007':'Verraco borrado correctamente'}


def rerror(codigo):

    respuesta = {
              'respuesta':'ERROR',
              'codigo':codigo,
              'descripcion':errores[codigo]
            }

    return respuesta


def rok(codigo):

    respuesta = {
            'respuesta':'OK',
            'codigo':codigo,
            'descripcion':oks[codigo]
        }

    return respuesta


