import dbConn as dbConn
from flask import jsonify, Blueprint, request 
from lib2to3.pgen2 import token
import json

posicao_bp = Blueprint('posicao', __name__)

db = dbConn.Db()

@posicao_bp.route('/json/<string:token>/id')
def ultimaPosicaoVeiculos(token):
    
    access = db.getTokenValido(token)

    if len(access) > 0:
        args = request.args
        posicoesLista = []
        
        for veiculo_id in args.getlist('id'):
            
            posicoes = db.getPosicoes(veiculo_id)
            
            if len(posicoes) > 0:
                posicoesLista.append({
                    "ponperidentify": int(posicoes['ID_POSICAO'][0]),
                    "veiid": int(posicoes['ID_VEICULO'][0]),
                    "ponperlati": posicoes['LAT'][0],
                    "ponperlong": posicoes['LON'][0],
                    "ponperdathor": posicoes['DATA_HORA'][0],
                    "ponpervel": int(posicoes['VELOCIDADE'][0]),
                    "ponpercruz": posicoes['ENDERECO'][0],
                    "ponperign": int(posicoes['IGNICAO'][0]),
                    "motorista": posicoes['CONDUTOR'][0],
                    "ponpervalid": 1,
                    "ponperdisper": posicoes['ODOMETRO'][0],
                    "eventos": [ posicoes['MOTIVO'][0] +' '+posicoes['MOTIVO_COMPLEMENTO'][0] ],
                    "minutosSemTransmissao": 0
                })
            
        ret = {
            "mensagem" : "SUCCESSFUL",
            "data" : posicoesLista
        }
    else:
        ret = {
            "mensagem" : "INVALID_TOKEN;"+token
        }

    return jsonify(ret)
