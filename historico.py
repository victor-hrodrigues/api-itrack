import dbConn as dbConn
from flask import jsonify, Blueprint, request 
from lib2to3.pgen2 import token
import json
import numpy as np
historico_bp = Blueprint('historico', __name__)

db = dbConn.Db()

@historico_bp.route('/json/<string:token>/<string:veiculo_id>/<string:data_ini>/<string:data_fim>')
def historico(token, veiculo_id, data_ini, data_fim):
    access = db.getTokenValido(token)

    if len(access) > 0:
        posicoes = db.getPosicoesDia(veiculo_id, data_ini, data_fim)
        posicoesLista = []

        for idx, row in posicoes.iterrows():

            # alteracao para substiturar NaN por None (null)
            row = row.replace({np.nan: None})

            posicoesLista.append({
                "ponperidentify": row['ID_POSICAO'],
                "veiid": row['ID_VEICULO'],
                "ponperlati": row['LAT'],
                "ponperlong": row['LON'],
                "ponperdathor": row['DATA_HORA'],
                "ponpervel": row['VELOCIDADE'],
                "ponpercruz": row['ENDERECO'],
                "ponperign": row['IGNICAO'],
                "motorista": row['CONDUTOR'],
                "ponpervalid": 1,
                "ponperdisper": row['ODOMETRO'],
                "eventos": [ row['MOTIVO'] ],
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


@historico_bp.route('/geojson/<string:token>/', methods = ['POST'])
def geojson(token):
    access = db.getTokenValido(token)

    if len(access) > 0:
        parameters = json.loads(request.get_data(as_text=True))
        veiids = parameters['veiids']
        data_ini = parameters['dataHoraInicio']
        data_fim = parameters['dataHoraFim']
        posicoesLista = []

        for veiculo_id in veiids:
            posicoes = db.getPosicoesGeo(veiculo_id, data_ini, data_fim)
            if len(posicoes) > 0:
                for idx, row in posicoes.iterrows():
                    posicoesLista.append((row['LAT'], row['LON']))

        ret = {
            "mensagem" : "SUCCESSFUL",
            "data": [{
                "type": "MultiPoint",
                "coordinates": posicoesLista
            }]
        }
    else:
        ret = {
            "mensagem" : "INVALID_TOKEN;"+token
        }

    return jsonify(ret)