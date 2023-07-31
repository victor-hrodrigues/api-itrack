import dbConn as dbConn
from flask import Blueprint, request, jsonify
from lib2to3.pgen2 import token

clientes_bp = Blueprint('clientes', __name__)

db = dbConn.Db()

@clientes_bp.route('/<string:cliente_id>/pontos-referencia/')
def lista_pontos_referencia(cliente_id):
    args = request.args
    token  = args['token']
    page    = 0
    size    = 10
    
    if "page" in args:
        if args["page"] != '':
            page = args["page"]
    if "size" in args:
        if args["size"] != '':
            size = args["size"]

    access = db.getTokenValido(token)
    if len(access) > 0:
        pr = db.getPontosReferencia(cliente_id, page, size)

        if len(pr) > 0:
            prLista = []
            for idx, row in pr.iterrows():
                row = row.fillna('')
                prLista.append({
                    'id': row['ID_PONTO_REFERENCIA'],
                    "cliid": row['ID_CLIENTE'],
                    "description": row['NOME'],
                    "lat": row['LAT'],
                    "lon": row['LON'],
                    "radius": row['RAIO']
                })

            ret = {
                "mensagem" : "SUCCESSFUL",
                "data" : prLista
            }
        else:
            ret = {
                "mensagem" : "DENIED;"
            }
    else:
        ret = {
            "mensagem" : "INVALID_TOKEN;"+token
        }

    return jsonify(ret)


@clientes_bp.route('/<string:cliente_id>/veiculos')
def lista_veiculos_filtrado_paginado(cliente_id):
    args = request.args
    token = args['token']
    page    = 0
    size    = 10
    q       = ''
    gps     = ''
    ign     = ''
    minVel  = ''
    semTransmissao = ''

    if "page" in args:
        if args["page"] != '':
            page = args["page"]
    if "size" in args:
        if args["size"] != '':
            size = args["size"]
    if "q" in args:
        q = str(args["q"])
    if "gps" in args:
        gps = args["gps"]
    if "ign" in args:
        ign = args["ign"]
    if "minVel" in args:
        minVel = args["minVel"]
    if "semTransmissao" in args:
        semTransmissao = args["semTransmissao"]
    
    access = db.getTokenValido(token)

    if len(access) > 0:
        veiculos = db.getVeiculosFiltro(cliente_id, page, size, q, gps, ign, minVel, semTransmissao)
        veiculosLista = []
        
        if len(veiculos) > 0:
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
