"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, Personaje, Planeta, Usuario, Favorito
import json
#from models import Person
#import JWT
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager



app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Setup the Flask-JWT-Extended extension
app.config["JWT_SECRET_KEY"] = "super-secret"  # Change this!
jwt = JWTManager(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)


# # ENDPOINTS

# @app.route('/user', methods=['GET'])
# def handle_hello():

#     response_body = {
#         "msg": "Hello, this is your GET /user response "
#     }

#     return jsonify(response_body), 200


# ENDPOINT PARA TODOS LOS PERSONAJES
@app.route('/personaje', methods=['GET'])
def get_all_personaje():

    personaje = Personaje.query.all() # esto obtiene todos los registros de la tabla User
    results = list(map(lambda item: item.serialize(), personaje)) #esto serializa los datos del arrays users
    return jsonify(results), 200

# ENDPOINT PARA 1 PERSONAJE
@app.route('/personaje/<int:personaje_id>', methods=['GET'])
def get_personaje(personaje_id):

    personaje = Personaje.query.filter_by(id=personaje_id).first()
    return jsonify(personaje.serialize()), 200


# ENDPOINT PARA TODOS LOS PLANETAS
@app.route('/planeta', methods=['GET'])
def get_all_planeta():

    planeta = Planeta.query.all() # esto obtiene todos los registros de la tabla User
    results = list(map(lambda item: item.serialize(), planeta)) #esto serializa los datos del arrays users
    return jsonify(results), 200

# ENDPOINT PARA 1 Planeta
@app.route('/planeta/<int:planeta_id>', methods=['GET'])
def get_planeta(planeta_id):

    planeta = Planeta.query.filter_by(id=planeta_id).first()
    return jsonify(planeta.serialize()), 200


# ENDPOINT PARA CREAR 1 USUARIO
@app.route('/usuario', methods=['POST'])
def create_usuario():
    body = json.loads(request.data)
    
    query_usuario = Usuario.query.filter_by(email=body["email"]).first()
   

    if query_usuario is None:
        #guardar datos recibidos a la tabla User
        new_usuario = Usuario(
            
            first_name=body["first_name"],
            last_name=body["last_name"],
            email=body["email"],
            password=body["password"],
        )
            
        db.session.add(new_usuario)
        db.session.commit()
        response_body = {
                "msg": "created usuario"
            }
        return jsonify(response_body), 200

        esponse_body = {
            "msg": "existed user"
        }
    return jsonify(response_body), 400

@app.route('/usuario/<int:usuario_id>', methods=['GET'])
def get_usuario(usuario_id):

    response_body = {
        "msg": "Aqui esta su usuario"
    }
    return jsonify(response_body), 200


# ENDPOINT FAVORITOS
@app.route('/usuario/<int:usuario_id>/favorito', methods=['GET'])
def get_all_favorito(usuario_id):
    

    favorito = Favorito.query.filter_by(usuario_id = usuario_id).all() # esto obtiene todos los registros de la tabla User
    results = list(map(lambda item: item.serialize(), favorito)) #esto serializa los datos del arrays users

    return jsonify(results), 200


#DELETE
@app.route('/usuario/<int:usuario_id>/favorito/planeta', methods=['DELETE'])
def delete_favorito_planet(usuario_id):
    body = json.loads(request.data)

    query_favorito_planeta = Favorito.query.filter_by(planeta_id=body["planeta_id"],usuario_id=body["usuario_id"]).first()
    print(query_favorito_planeta)

    if query_favorito_planeta  is not None:
        delete_planeta_favorito = query_favorito_planeta
        db.session.delete (delete_planeta_favorito)
        db.session.commit()

        response_body = {
                "msg": "deleted planeta favorito"
            }

        return jsonify(response_body), 200

        response_body = {
                "msg": "planeta favorito no existe"
            }

        return jsonify(response_body), 200


# Create a route to authenticate your users and return JWTs. The
# create_access_token() function is used to actually generate the JWT.
@app.route("/login", methods=["POST"])

def login():
    email = request.json.get("email", None)
    password = request.json.get("password", None)

    usuario = Usuario.query.filter_by(email=email).first()

    if usuario is None:
        return jsonify({"msg": "Bad username or password"}), 404 

    if email != usuario.email or password != usuario.password:
        return jsonify({"msg": "Bad username or password"}), 401

    
    access_token = create_access_token(identity=email)

    response_body= {

        "access_token" : access_token,
        "usuario": usuario.serialize()

        }
    return jsonify(response_body) , 200


# Protect a route with jwt_required, which will kick out requests
# without a valid JWT present.

@app.route("/profile", methods=["GET"])
@jwt_required()
def protected():

    # Access the identity of the current user with get_jwt_identity
    current_user = get_jwt_identity()

    usuario = Usuario.query.filter_by(email=current_user).first()

    if usuario is None:
        return jsonify({"msg": "User not exist"}), 404 

    response_body = {

        "usuario": usuario.serialize()

    }

    return jsonify(response_body), 200

    





# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
