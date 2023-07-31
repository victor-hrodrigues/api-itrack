from flask import Blueprint, request, jsonify
import dbConn as dbConn
import hashlib
import json

db = dbConn.Db()

logout_bp = Blueprint('logout', __name__)

@logout_bp.route('/', methods = ['POST'])
def logout():
    request_data = request.get_json()
    deviceId = request_data["deviceId"]

    if deviceId != '':
        db.logoutUsuario(deviceId)
    
        ret = {
            "mensagem" : "SUCCESSFUL"
        }
    else:
        ret = {
            "mensagem" : "DENIED;"
        }
    
    return jsonify(ret)
