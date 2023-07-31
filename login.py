from os import set_inheritable
from flask import Blueprint, request, jsonify
import dbConn as dbConn
import hashlib
import json

db = dbConn.Db()

login_bp = Blueprint('login', __name__)

@login_bp.route('/', methods = ['POST'])

def login():
    request_data = request.get_json()
    login = request_data["username"]
    password = request_data["password"]
    deviceId = ''
    if "deviceId" in request_data:
        deviceId = request_data["deviceId"]

    if login != '' and password != '':
        senha = db.hashPassword(request_data["username"], request_data["password"])

        user = db.getUsuario(login, senha)

        if len(user) > 0:
            token = hashlib.md5(str(login).encode('utf-8'))
            token_hex = token.hexdigest()

            db.loginUsuario(user['ID_USUARIO'][0], token_hex, deviceId)
        
            ret = {
                "mensagem"      : "SUCCESSFUL", 
                "token"         : token_hex, 
                "refreshToken"  : "",
                "nome"          : user['NOME'][0]
            }
        else:
            ret = {
                "mensagem" : "DENIED;"
            }
    else:
        ret = {
            "mensagem" : "DENIED;"
        }

    return jsonify(ret)
