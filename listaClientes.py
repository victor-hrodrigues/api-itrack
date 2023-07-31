import dbConn as dbConn
from flask import Blueprint, jsonify
from lib2to3.pgen2 import token

listaClientes_bp = Blueprint('listaClientes', __name__)

db = dbConn.Db()

@listaClientes_bp.route('/json/simples/<string:token>/')
def lista(token):
    access = db.getTokenValido(token)

    if len(access) > 0:
        empresas = db.getEmpresas(access['EMPRESA'][0])
        empresasLista = []

        for idx, row in empresas.iterrows():
            empresasLista.append({
                'id_cliente' : row['ID_CLIENTE'],
                'nome_cliente' : row['NOME_CLIENTE']
            })

        ret = {
            "mensagem" : "SUCCESSFUL",
            "data" : empresasLista
        }
    else:
        ret = {
            "mensagem" : "INVALID_TOKEN;"+token
        }

    return jsonify(ret)
