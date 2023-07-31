import dbConn as dbConn
from flask import Blueprint, jsonify, request
from lib2to3.pgen2 import token
import json

veiculos_bp = Blueprint('veiculos', __name__)

db = dbConn.Db()

@veiculos_bp.route('/<string:veiculo_id>/posicoes/<string:data_hora>')
def posicao_veiculo_especifica(veiculo_id, data_hora):
    args = request.args
    token = args['token']
    
    access = db.getTokenValido(token)

    if len(access) > 0:
        posicoes = db.getPosicoesDiaDataHora(veiculo_id, data_hora)
            
        if len(posicoes) > 0:
            posicoesLista = []
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
                "eventos": [ posicoes['MOTIVO'][0] +' - '+posicoes['MOTIVO_COMPLEMENTO'][0] ],
                "minutosSemTransmissao": 0,
                "ponperhorim": posicoes['HORIMETRO'][0],
                "ponperten": posicoes['BATERIA'][0],
                "ponpertem": posicoes['TEMPERATURA1'][0]
            })
            
            ret = {
                "mensagem" : "SUCCESSFUL",
                "data" : posicoesLista
            }
        else:
            ret = {
                "mensagem" : "ERROR;"
            }
    else:
        ret = {
            "mensagem" : "INVALID_TOKEN;"+token
        }

    return jsonify(ret)


@veiculos_bp.route('/<string:veiculo_id>/comandos-enviados/')
def lista_comandos_enviados(veiculo_id):
    args = request.args
    token = args['token']
    data_ini = args['ini']
    data_fim = args['fim']
    
    access = db.getTokenValido(token)

    if len(access) > 0:
        cmdEnviados = db.getComandosEnviados(veiculo_id, data_ini, data_fim)

        if len(cmdEnviados) > 0:
            cmdEnviadosLista = []

            for idx, row in cmdEnviados.iterrows():

                cmdParamLista = ''
                cmdParams = db.getComandosEnviadosParametros(row['ID'])
                if len(cmdParams) > 0:
                    for idx2, row2 in cmdParams.iterrows():
                        cmdParamLista += "- " + row2['NOME'] + ": " + row2['VALOR'] + " "

                cmdEnviadosLista.append({
                    'id': row['ID'],
                    "descricao": row['FUNCIONALIDADE'],
                    "gravacao": row['DATA'],
                    "agendamento": row['DATA'],
                    "envio": row['DATA_ENVIO'],
                    "recebimento": row['DATA_ENVIO'],
                    "tentativas": 1,
                    "status": "Comando Enviado",
                    "valor": cmdParamLista,
                    "usuario": row['USUARIO'],
                    "veiid": row['ID_VEICULO']
                })

            ret = {
                "mensagem" : "SUCCESSFUL",
                "data" : cmdEnviadosLista
            }
        else:
            ret = {
                "mensagem" : "SUCCESSFUL",
                "data" : []
            }
    else:
        ret = {
            "mensagem" : "INVALID_TOKEN;"+token
        }

    return jsonify(ret)


@veiculos_bp.route('/<string:veiculo_id>/comandos-disponiveis/')
def lista_comandos_disponiveis(veiculo_id):
    args = request.args
    token = args['token']
    
    access = db.getTokenValido(token)
    if len(access) > 0:
        comandos = db.getComandos(veiculo_id, access['ID_USUARIO'][0])

        if len(comandos) > 0:
            comandosLista = []

            for idx, row in comandos.iterrows():
                comandosLista.append({
                    'id': row['ID'],
                    "descricao": row['NOME'],
                    "tipoOpcao": 'OPCOES_INDEPENDENTES'
                })

            ret = {
                "mensagem" : "SUCCESSFUL",
                "data" : comandosLista
            }
        else:
            ret = {
                "mensagem" : "ERROR;"
            }
    else:
        ret = {
            "mensagem" : "INVALID_TOKEN;"+token
        }

    return jsonify(ret)


@veiculos_bp.route('/<string:veiculo_id>/comandos-disponiveis/<string:comando_id>/opcoes')
def lista_comandos_disponiveis_parametros(veiculo_id, comando_id):
    args = request.args
    token = args['token']
    
    access = db.getTokenValido(token)
    if len(access) > 0:
        parametros = db.getComandosParametros(comando_id)

        if len(parametros) > 0:
            parametrosLista = []

            for idx, row in parametros.iterrows():
                parametrosLista.append({
                    'id': row['ID'],
                    "descricao": row['NOME']
                })

            ret = {
                "mensagem" : "SUCCESSFUL",
                "data" : parametrosLista
            }
        else:
            ret = {
                "mensagem" : "ERROR;"
            }
    else:
        ret = {
            "mensagem" : "INVALID_TOKEN;"+token
        }

    return jsonify(ret)


@veiculos_bp.route('/<string:veiculo_id>/comandos-enviados/', methods = ['POST'])
def envia(veiculo_id):
    args = request.args
    token = args['token']

    request_data = request.get_json()
    id_comando = request_data["idComando"]
    parametros = request_data["parametros"]
    
    access = db.getTokenValido(token)
    if len(access) > 0:
        veiculo = db.getVeiculo(veiculo_id)
            
        if len(veiculo) > 0:

            seq = db.getComandoSequence()
            if len(seq) > 0:

                id_cmd_espera = seq['ID'][0]

                for idx, row in parametros.items():
                    param_id = idx
                    if row == True:
                        param_vl = 'Sim'
                    else:
                        param_vl = 'Nao'
                        
                comando = db.gravaComando(id_cmd_espera, id_comando, veiculo['ID_EQUIPAMENTO'][0], veiculo['SERIAL'][0], access['LOGIN'][0], param_vl, veiculo['APARELHO'][0], veiculo['APARELHO_NOME'][0])
                if comando:
                    parametro = db.gravaParametros(id_cmd_espera, idx, param_vl)

                    ret = {
                        "mensagem" : "SUCCESSFUL",
                        "data" : []
                    }
                else:
                    ret = {
                        "mensagem" : "ERROR;"
                    }

            else:
                ret = {
                    "mensagem" : "ERROR;"
                }
        else:
            ret = {
                "mensagem" : "ERROR;"
            }

    else:
        ret = {
            "mensagem" : "INVALID_TOKEN;"+token
        }

    return jsonify(ret)


@veiculos_bp.route('/<string:veiculo_id>/estacione-seguro', methods = ['POST'])
def cria_estacione_seguro(veiculo_id):
    args = request.args
    token = args['token']
    
    request_data = request.get_json()
    raio_ativa_bool = request_data["fenceActivation"]
    ignicao_ativa_bool = request_data["ignitionActivation"]

    access = db.getTokenValido(token)
    if len(access) > 0:

        posicao = db.getPosicoes(veiculo_id)
        if len(posicao) > 0:

            seq = db.getAncoraSequence()
            if len(seq) > 0:

                if raio_ativa_bool == True:
                    raio_ativa = 1
                else:
                    raio_ativa = 0

                if ignicao_ativa_bool == True:
                    ignicao_ativa = 1
                else:
                    ignicao_ativa = 0

                id_ancora = seq['ID'][0]
            
                ancora = db.gravaAncora(id_ancora, veiculo_id, raio_ativa, ignicao_ativa, posicao["LAT"][0], posicao["LON"][0], access["ID_USUARIO"][0])

                if ancora:
                    ret = {
                        "mensagem" : "SUCCESSFUL",
                        "data" : [{
                            "id" : int(id_ancora),
                            "fenceActivation" : bool(raio_ativa_bool),
                            "ignitionActivation" : bool(ignicao_ativa_bool),
                            "veiid" : int(veiculo_id),
                            "creatorId" : int(access["ID_USUARIO"][0]),
                            "creatorName" : access["NOME"][0],
                            "isCreator" : bool(True),
                            "isListening" : bool(True),
                            "lat" : float(posicao["LAT"][0]),
                            "lon" : float(posicao["LON"][0]),
                            "radius" : float(100)
                        }]
                    }
                else:
                    ret = {
                        "mensagem" : "ERROR;"
                    }
            else:
                ret = {
                    "mensagem" : "ERROR;"
                }
        else:
            ret = {
                "mensagem" : "ERROR;"
            }
    else:
        ret = {
            "mensagem" : "INVALID_TOKEN;"+token
        }

    return jsonify(ret)


@veiculos_bp.route('/<string:veiculo_id>/estacione-seguro/<string:ancora_id>', methods = ['DELETE'])
def deleta_estacione_seguro(veiculo_id, ancora_id):
    args = request.args
    token = args['token']
    
    access = db.getTokenValido(token)
    if len(access) > 0:

        usuarioCriacao = db.getAncoraId(ancora_id)
        if len(usuarioCriacao) > 0:
            # somente o mesmo usuario que criou pode excluir a ancora (se for o mesmo exclui)
            if int(usuarioCriacao["CREATED_BY"][0]) == int(access["ID_USUARIO"][0]):
                deteteAncora = db.delAncora(ancora_id)
                if deteteAncora:
                    ret = {
                        "mensagem" : "SUCCESSFUL",
                        "data": []
                    }
                else:
                    ret = {
                        "mensagem" : "ERROR;"
                    }
            else:
                ret = {
                    "mensagem" : "DENIED;",
                    "data": []
                }
        else:
            ret = {
                "mensagem" : "ERROR;"
            }
    else:
        ret = {
            "mensagem" : "INVALID_TOKEN;"+token
        }

    return jsonify(ret)


@veiculos_bp.route('/<string:veiculo_id>/viagens/')
def lista_viagens(veiculo_id):
    args = request.args
    token = args['token']
    data_ini = args['ini']
    data_fim = args['fim']
    
    access = db.getTokenValido(token)

    if len(access) > 0:
        viagens = db.getViagens(veiculo_id, data_ini, data_fim)

        if len(viagens) > 0:
            viagensLista = []

            for idx, row in viagens.iterrows():
                viagensLista.append({
                    'dataHoraIni': row['INICIO_FORMAT'],
                    "dataHoraFim": row['FIM_FORMAT'],
                    "veiid": row['VEIID'],
                    "distanciaEmMetros": float(row['DISTANCIA']),
                    "tempoTotalEmMinutos": row['TEMPO'],
                    "enderecoIni": row['SAIDA_DE'],
                    "enderecoFim": row['CHEGOU_EM']
                })

            ret = {
                "mensagem" : "SUCCESSFUL",
                "data" : viagensLista
            }
        else:
            ret = {
                "mensagem" : "SUCCESSFUL",
                "data" : []
            }
    else:
        ret = {
            "mensagem" : "INVALID_TOKEN;"+token
        }

    return jsonify(ret)