from flask import Blueprint


bp_main = Blueprint('main', __name__, url_prefix='/')
bp_tomograph = Blueprint('tomograph', __name__, url_prefix='/tomograph')


@bp_main.route('/', methods=['GET'])
def main_route():
    return 'Experiment mock'


@bp_tomograph.route('/', methods=['GET'])
def tomograph():
    return 'TOMOGRAPH'
