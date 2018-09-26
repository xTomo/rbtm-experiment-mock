from flask import (
    Blueprint, request, send_file
)
import json
from .tomograph import Tomograph
from .modExpError import ModExpError


FRAME_PNG_FILENAME = 'image.png'


bp_main = Blueprint('main', __name__, url_prefix='/')
bp_tomograph = Blueprint('tomograph', __name__, url_prefix='/tomograph/<int:tomo_num>')

tomograph = Tomograph()

# Base routes
@bp_main.route('/', methods=['GET'])
def main_route():
    return 'RBTM experiment mock'


@bp_tomograph.route('/', methods=['GET'])
def tomograph(tomo_num):
    return 'TOMOGRAPH {}'.format(tomo_num)


# State route
@bp_tomograph.route('/state', methods=['GET'])
def check_state(tomo_num):
    return request.url


# Source routes
@bp_tomograph.route('/source/power-on', methods=['GET'])
def source_power_on(tomo_num):
    return request.url


@bp_tomograph.route('/source/power-off', methods=['GET'])
def source_power_off(tomo_num):
    return request.url


@bp_tomograph.route('/source/set-voltage', methods=['POST'])
def source_set_voltage(tomo_num):
    return request.url


@bp_tomograph.route('/source/set-current', methods=['POST'])
def source_set_current(tomo_num):
    return request.url


@bp_tomograph.route('/source/get-voltage', methods=['GET'])
def source_get_voltage(tomo_num):
    return request.url


@bp_tomograph.route('/source/get-current', methods=['GET'])
def source_get_current(tomo_num):
    return request.url


# Shutter routes
@bp_tomograph.route('/shutter/open/<int:time_>', methods=['GET'])
def shutter_open(tomo_num, time_):
    return request.url


@bp_tomograph.route('/shutter/close/<int:time_>', methods=['GET'])
def shutter_close(tomo_num, time_):
    return request.url


@bp_tomograph.route('/shutter/state', methods=['GET'])
def shutter_state(tomo_num):
    return request.url


# Motor routes
@bp_tomograph.route('/motor/set-horizontal-position', methods=['POST'])
def motor_set_horizontal_position(tomo_num):
    return request.url


@bp_tomograph.route('/motor/set-vertical-position', methods=['POST'])
def motor_set_vertical_position(tomo_num):
    return request.url


@bp_tomograph.route('/motor/set-angle-position', methods=['POST'])
def motor_set_angle_position(tomo_num):
    return request.url


@bp_tomograph.route('/motor/get-horizontal-position', methods=['GET'])
def motor_get_horizontal_position(tomo_num):
    return request.url


@bp_tomograph.route('/motor/get-vertical-position', methods=['GET'])
def motor_get_vertical_position(tomo_num):
    return request.url


@bp_tomograph.route('/motor/get-angle-position', methods=['GET'])
def motor_get_angle_position(tomo_num):
    return request.url


@bp_tomograph.route('/motor/move-away', methods=['GET'])
def motor_move_away(tomo_num):
    return request.url


@bp_tomograph.route('/motor/move-back', methods=['GET'])
def motor_move_back(tomo_num):
    return request.url


@bp_tomograph.route('/motor/reset-angle-position', methods=['GET'])
def motor_reset_angle_position(tomo_num):
    return request.url


# Detector routes
@bp_tomograph.route('/detector/get-frame', methods=['POST'])
def detector_get_frame(tomo_num):
    return request.url


@bp_tomograph.route('/detector/get-frame-with-closed-shutter', methods=['POST'])
def detector_get_frame_with_closed_shutter(tomo_num):
    return request.url


@bp_tomograph.route('/detector/chip_temp', methods=['GET'])
def detector_get_chip_temperature(tomo_num):
    return request.url


@bp_tomograph.route('/detector/hous_temp', methods=['GET'])
def detector_get_hous_temperature(tomo_num):
    return request.url


# Experiment routes
@bp_tomograph.route('/experiment/start', methods=['POST'])  # TODO: POST?
def experiment_start(tomo_num):
    return request.url


@bp_tomograph.route('/experiment/stop', methods=['GET'])  # TODO: GET?
def experiment_stop(tomo_num):
    return request.url


# functions
def create_response(success=True, exception_message='', error='', result=None):
    response_dict = {
        'success': success,
        'exception message': exception_message,
        'error': error,
        'result': result,
    }
    return json.dumps(response_dict)


def call_method_create_response(tomo_num, method_name, args=(), GET_FRAME_method=False):

    if type(args) not in (tuple, list):
        args = (args,)

    try:
        result = getattr(tomograph, method_name)(*args)
    except ModExpError as e:
        return e.create_response()

    if not GET_FRAME_method:
        return create_response(success=True, result=result)
    else:
        return send_file('../' + FRAME_PNG_FILENAME, mimetype='image/png')
