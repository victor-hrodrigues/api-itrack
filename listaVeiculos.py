import dbConn as dbConn
from flask import Blueprint, jsonify
from lib2to3.pgen2 import token
import json

listaVeiculos_bp = Blueprint('listaVeiculos', __name__)

db = dbConn.Db()

@listaVeiculos_bp.route('/json/<string:token>/<string:cliente_id>')
def simples(token, cliente_id):
    access = db.getTokenValido(token)

    if len(access) > 0:
        veiculos = db.getVeiculos(cliente_id)
        veiculosLista = []

        for idx, row in veiculos.iterrows():
            row = row.fillna('') # remove os Nan

            if int(row['TIPO']) == 1:
                img = 'imgtemp/img16.png'
            elif int(row['TIPO']) == 8: 
                img = 'imgtemp/img24.png'
            elif int(row['TIPO']) == 16: 
                img = 'imgtemp/img5.png'
            elif int(row['TIPO']) == 37: 
                img = 'imgtemp/img45.png'
            elif int(row['TIPO']) == 3 or int(row['TIPO']) == 22: 
                img = 'imgtemp/img18.png'
            elif int(row['TIPO']) == 23 or int(row['TIPO']) == 24: 
                img = 'imgtemp/img7.png'
            elif int(row['TIPO']) == 40 or int(row['TIPO']) == 43: 
                img = 'imgtemp/img14.png'
            elif int(row['TIPO']) == 41 or int(row['TIPO']) == 44: 
                img = 'imgtemp/img26.png'
            elif int(row['TIPO']) == 4 or int(row['TIPO']) == 15 or int(row['TIPO']) == 17: 
                img = 'imgtemp/img9.png'
            else:
                img = 'imgtemp/img10.png'

            veiculosLista.append({
                'veiid': row['ID_VEICULO'],
                'veiign': row['IGNICAO'],
                'veipla': row['PLACA'],
                'veides': row['PLACA'],
                'veiimg': img,
                'disid': row['SERIAL'],
                'clinom': row['CLIENTE_NOME'],
                'imei': None,
                'cpfcnpj': row['CPF_CNPJ'],
                'cliid': row['ID_CLIENTE'],
                'ultimoPontoMini': {
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
                }
            })

        ret = {
            "mensagem" : "SUCCESSFUL",
            "data" : veiculosLista
        }
    else:
        ret = {
            "mensagem" : "INVALID_TOKEN;"+token
        }

    return jsonify(ret)
