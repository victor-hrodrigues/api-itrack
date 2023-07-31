from flask import Blueprint
teste_bp = Blueprint('teste', __name__)


@teste_bp.route('/')
def teste():
    return "Hello from Home Pagee"
