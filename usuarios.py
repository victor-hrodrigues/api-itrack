import dbConn as dbConn
from flask import Blueprint, jsonify, request
from lib2to3.pgen2 import token
import json
import string
import random

usuarios_bp = Blueprint('usuarios', __name__)

db = dbConn.Db()

@usuarios_bp.route('/me/senha', methods = ['PUT'])
def altera_senha():
    args = request.args
    token = args['token']

    request_data = request.get_json()
    novaSenha = request_data["novaSenha"]
    senhaAtual = request_data["senhaAtual"]

    access = db.getTokenValido(token)

    if len(access) > 0:
        if(len(novaSenha) > 7):
            novaSenhaMD5 = db.hashPassword(access["LOGIN"][0], novaSenha)
            db.alteraSenhaUsuario(access['ID_USUARIO'][0], novaSenhaMD5)
            ret = {
                "mensagem" : "SUCCESSFUL",
                "data" : []
            }
        else:
            ret = {
                "mensagem" : "INVALID_PARAMS;A senha deve conter 8 caracteres ou mais."
            }  
    else:
        ret = {
            "mensagem" : "INVALID_TOKEN;"+token
        }

    return jsonify(ret)


@usuarios_bp.route('/<string:login>/recuperacao-senha/opcoes')
def recuperacao_senha_opcao(login):
    #verifica se usuario possui email para ser viando para a recuperacao de senha
    usuario = db.getUsuarioLogin(login)
    
    if len(usuario) > 0:
        email = usuario["EMAIL"][0]
        if len(email) > 0:
            masc = ''
            for x in range(len(email)-14):
                if x < 10:
                    masc = masc+'*'
            emailMascara = email[:5]+masc+email[-9:]

            data = {
                "id":"EMAIL",
                "nome":"Por Email",
                "descricao":"Um código será enviado no email "+emailMascara
            }

            ret = {
                "mensagem" : "SUCCESSFUL",
                "data" : [data]
            }
        else:
            ret = {
                "mensagem" : "SUCCESSFUL",
                "data" : []
            }
    else:
        ret = {
            "mensagem" : "SUCCESSFUL",
            "data" : []
        }

    return jsonify(ret)

    
@usuarios_bp.route('/<string:login>/recuperacao-senha', methods = ['POST'])
def recuperacao_senha(login):
    request_data = request.get_json()
    opcao = request_data["opcao"] #email é fixo
    
    #verifica se usuario possui email para ser viando para a recuperacao de senha
    usuario = db.getUsuarioLogin(login)
    
    if len(usuario) > 0:
        email = usuario["EMAIL"][0]

        if email != None:
            if usuario["ITRACK_CODIGO_RECUPERACAO"][0] != None:
                codigo = usuario["ITRACK_CODIGO_RECUPERACAO"][0]
            else:
                # gera um codigo de 6 letras aleatorio
                codigo = ''.join(random.choice(string.ascii_uppercase) for _ in range(6))
                # salva o codigo no usuario para verificacao posterior
                db.salvaCodigoRecuperacao(usuario["ID_USUARIO"][0], codigo) 

            # envia email com o codigo
            db.enviaEmailRecuperacao(email, codigo)

            ret = {
                "mensagem" : "SUCCESSFUL",
                "data" : []
            }
        else:
            ret = {
                "mensagem" : "SUCCESSFUL",
                "data" : []
            }
    else:
        ret = {
            "mensagem" : "SUCCESSFUL",
            "data" : []
        }

    return jsonify(ret)


@usuarios_bp.route('/<string:login>/recuperacao-senha/nova-senha', methods = ['POST'])
def recuperacao_senha_resetar(login):
    request_data = request.get_json()
    codigo = request_data["codigo"]
    novaSenha = request_data["novaSenha"]
    
    #verifica se usuario possui email para ser viando para a recuperacao de senha
    usuario = db.getUsuarioLogin(login)
    
    if len(usuario) > 0:
        if usuario["ITRACK_CODIGO_RECUPERACAO"][0] != None and usuario["ITRACK_CODIGO_RECUPERACAO"][0] == codigo:
            
            if(len(novaSenha) > 7):
                novaSenhaMD5 = db.hashPassword(usuario["LOGIN"][0], novaSenha)
                db.alteraSenhaUsuario(usuario['ID_USUARIO'][0], novaSenhaMD5)
                ret = {
                    "mensagem" : "SUCCESSFUL",
                    "data" : []
                }
            else:
                ret = {
                    "mensagem" : "INVALID_PARAMS;A senha deve conter 8 caracteres ou mais."
                }  
        else:
            ret = {
                "mensagem" : "ERROR;O código não confere com o fornecido",
                "data" : []
            }
    else:
        ret = {
            "mensagem" : "ERROR",
            "data" : []
        }

    return jsonify(ret)