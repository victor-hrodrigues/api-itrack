from flask import Flask

#from teste import teste_bp

from login import login_bp
from logout import logout_bp
from listaClientes import listaClientes_bp
from listaVeiculos import listaVeiculos_bp
from veiculos import veiculos_bp 
from historico import historico_bp
from clientes import clientes_bp
from posicao import posicao_bp
from estacioneSeguro import estacioneSeguro_bp 
from usuarios import usuarios_bp 

app = Flask(__name__)

#app.register_blueprint(teste_bp, url_prefix='/teste')

app.register_blueprint(login_bp, url_prefix='/loginService')
app.register_blueprint(logout_bp, url_prefix='/loginService/logout')
app.register_blueprint(listaClientes_bp, url_prefix='/listaclientes')
app.register_blueprint(listaVeiculos_bp, url_prefix='/listaveiculos') #na api veiculos esta com o V em letra minuscula cuidar
app.register_blueprint(veiculos_bp, url_prefix='/veiculos')
app.register_blueprint(historico_bp, url_prefix='/historico')
app.register_blueprint(clientes_bp, url_prefix='/clientes')
app.register_blueprint(posicao_bp, url_prefix='/posicao')
app.register_blueprint(estacioneSeguro_bp, url_prefix='/estacione-seguro')
app.register_blueprint(usuarios_bp, url_prefix='/usuarios')

if __name__ == "__main__":
    app.run()
