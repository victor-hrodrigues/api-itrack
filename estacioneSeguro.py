import dbConn as dbConn
from flask import Blueprint, jsonify, request
from lib2to3.pgen2 import token
import json

estacioneSeguro_bp = Blueprint('estacioneSeguro', __name__)

db = dbConn.Db()

@estacioneSeguro_bp.route('/')
def lista_estacione_seguro():
    args = request.args
    token = args['token']
    
    access = db.getTokenValido(token)

    if len(access) > 0:
        ancoraLista = []
        
        for veiculo_id in args.getlist('veiids'):
            ancora = db.getAncoras(veiculo_id)
            
            if len(ancora) > 0:
                ancoraLista.append({
                    "veiid": int(veiculo_id),
                    "estacioneSeguro": {
                        "id" : int(ancora["ID"][0]),
                        "fenceActivation" : bool(int(ancora["RAIO_ATIVO"][0])),
                        "ignitionActivation" : bool(int(ancora["IGNICAO_ATIVO"][0])),
                        "veiid" : int(veiculo_id),
                        "creatorAt" : ancora["CREATED_AT"][0],
                        "creatorId" : int(ancora["CREATED_BY"][0]),
                        "creatorName" : ancora["NOME"][0],
                        "isCreator" : bool(int(ancora["USUARIO_ECRIADOR"][0])),
                        "isListening" : bool(int(ancora["USUARIO_MONITORANDO"][0])),
                        "lat" : float(ancora["LAT"][0]),
                        "lon" : float(ancora["LON"][0]),
                        "radius" : float(ancora["RAIO"][0])
                    }
                })
            else:
                 ancoraLista.append({
                    "veiid": int(veiculo_id),
                    "estacioneSeguro": None
                })
                
        ret = {
            "mensagem" : "SUCCESSFUL",
            "data" : ancoraLista
        }
    else:
        ret = {
            "mensagem" : "INVALID_TOKEN;"+token
        }

    return jsonify(ret)
