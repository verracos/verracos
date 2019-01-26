from setuptools import setup

setup(name='Verracos',
      version='1.0.3',
      description='Aplicacion que permite localizar Verracos en Avila',
      author='Victor Cuervo',
      author_email='vcuervo@gmail.com',
      url='http://www.python.org/sigs/distutils-sig/',
      install_requires=['Flask>=0.12.3','pymongo>=3.2','tinys3>=0.1.11','Flask-Mail==0.9.1']
     )
