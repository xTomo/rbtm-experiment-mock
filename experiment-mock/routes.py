from flask import Blueprint


bp_main = Blueprint('main', __name__, url_prefix='/')
bp_tomograph = Blueprint('tomograph', __name__, url_prefix='/tomograph/<int:tomo_num>')


# Base routes
@bp_main.route('/', methods=['GET'])
def main_route():
    return 'RBTM experiment mock'


@bp_tomograph.route('/', methods=['GET'])
def tomograph(tomo_num):
    return 'TOMOGRAPH {}'.format(tomo_num)


