import threading, time, json, requests
from io import BytesIO
from random import randint
import numpy as np
from scipy.ndimage import zoom
import matplotlib.pyplot as plt

from .constants import *


class ModExpError(Exception):
    def __init__(self, error, exception_message='', stop_msg=EMERGENCY_STOP_MSG):
        self.message = error
        self.error = error
        self.exception_message = exception_message
        self.stop_msg = stop_msg

    def __str__(self):
        return repr(self.message)

    def to_event_dict(self, exp_id):
        return create_event(event_type='message',
                            exp_id=exp_id,
                            MoF=self.stop_msg,
                            error=self.error,
                            exception_message=self.exception_message)

    def create_response(self):
        response_dict = {
            'success': False,
            'exception message': self.exception_message,
            'error': self.error,
            'result': None,
        }
        return json.dumps(response_dict)


def create_event(event_type, exp_id, MoF, exception_message='', error=''):
    if event_type == 'message':
        return {
            'type': event_type,
            'exp_id': exp_id,
            'message': MoF,
            'exception message': exception_message,
            'error': error,
        }

    elif event_type == 'frame':
        return {
            'type': event_type,
            'exp_id': exp_id,
            'frame': MoF,
        }

    return None


class Experiment:
    def __init__(self, tomograph, exp_param, FOSITW=5):
        self.tomograph = tomograph
        self.exp_id = exp_param['exp_id']

        self.DARK_count = exp_param['DARK']['count']
        self.DARK_exposure = exp_param['DARK']['exposure']

        self.EMPTY_count = exp_param['EMPTY']['count']
        self.EMPTY_exposure = exp_param['EMPTY']['exposure']

        self.DATA_step_count = exp_param['DATA']['step count']
        self.DATA_exposure = exp_param['DATA']['exposure']
        self.DATA_angle_step = exp_param['DATA']['angle step']
        self.DATA_count_per_step = exp_param['DATA']['count per step']
        self.DATA_delay = exp_param['DATA']['delay']

        frames_total_count = self.DARK_count + self.EMPTY_count + self.DATA_step_count * self.DATA_count_per_step
        self.total_digits_count = len(str(abs(frames_total_count - 1)))

        self.FOSITW = FOSITW

        self.frame_num = 0
        self.to_be_stopped = False
        self.stop_exception = None

    def get_and_send_frame(self, exposure, mode):

        if mode == 'dark':
            raw_image_with_metadata = self.tomograph.get_frame(exposure=exposure, with_open_shutter=False,
                                                               from_experiment=True)
        else:
            raw_image_with_metadata = self.tomograph.get_frame(exposure=exposure, with_open_shutter=True,
                                                               from_experiment=True)
        # frame_dict = {  u'image_data':  {   'image': np.empty((10, 10)),    },  }

        raw_image_with_metadata['mode'] = mode
        raw_image_with_metadata['number'] = str(self.frame_num).zfill(self.total_digits_count)

        send_to_webpage = (self.frame_num % self.FOSITW == 0)
        self.frame_num += 1

        # prepare_send_frame(raw_image_with_metadata,self,send_to_webpage)
        thr = threading.Thread(target=prepare_send_frame, args=(raw_image_with_metadata, self, send_to_webpage))
        thr.start()

    def run(self):
        self.to_be_stopped = False
        self.stop_exception = None
        self.tomograph.source_power_on(from_experiment=True)
        self.collect_dark_frames()
        self.collect_empty_frames()
        self.collect_data_frames()
        self.tomograph.source_power_off(from_experiment=True)
        return

    def collect_data_frames(self):
        initial_angle = self.tomograph.get_angle(from_experiment=True)
        initial_angle = initial_angle if initial_angle is not None else 0
        self.tomograph.set_exposure(self.DATA_exposure, from_experiment=True)
        data_angles = np.round((np.arange(0, self.DATA_step_count)) * self.DATA_angle_step + initial_angle, 2) % 360

        exp_angles = data_angles

        self.tomograph.move_back(from_experiment=True)
        self.tomograph.open_shutter(0, from_experiment=True)
        for current_angle in exp_angles:
            self.check_source()
            self.tomograph.set_angle(float(current_angle), from_experiment=True)

            for j in range(0, self.DATA_count_per_step):
                self.get_and_send_frame(exposure=None, mode='data')
                time.sleep(self.DATA_delay)

        self.tomograph.close_shutter(0, from_experiment=True)

    def collect_empty_frames(self):
        self.tomograph.move_away(from_experiment=True)
        self.tomograph.set_exposure(self.EMPTY_exposure, from_experiment=True)
        self.tomograph.open_shutter(0, from_experiment=True)
        for i in range(0, self.EMPTY_count):
            self.check_source()
            self.get_and_send_frame(exposure=None, mode='empty')
        self.tomograph.close_shutter(0, from_experiment=True)
        self.tomograph.move_back(from_experiment=True)

    def collect_dark_frames(self):
        self.tomograph.close_shutter(0, from_experiment=True)
        time.sleep(1.0)
        self.tomograph.set_exposure(self.DARK_exposure, from_experiment=True)
        for i in range(0, self.DARK_count):
            self.get_and_send_frame(exposure=None, mode='dark')

    def check_source(self):

        current = self.tomograph.source_get_current(from_experiment=True)
        voltage = self.tomograph.source_get_voltage(from_experiment=True)

        if (current is not None) and (voltage is not None):
            if current > 2 and voltage > 2:
                return

        print('X-ray source in wrong mode, try restart (off/on)')
        print('current = {0}, voltage = {1}'.format(current, voltage))

        self.tomograph.source_power_off(from_experiment=True)
        time.sleep(5)
        self.tomograph.source_power_on(from_experiment=True)
        time.sleep(5)


# Frame functions
def prepare_send_frame(raw_image_with_metadata, experiment, send_to_webpage=False):
    raw_image = raw_image_with_metadata['image_data']['raw_image']
    del raw_image_with_metadata['image_data']['raw_image']
    frame_metadata = raw_image_with_metadata

    try:
        # experiment = 1
        try:
            # image_numpy = np.zeros((100, 100))
            image_numpy = np.random.randint(0, randint(0, 65535), (2500, 2500))
        except Exception as e:
            raise ModExpError(error='Could not convert raw image to numpy.array', exception_message=e.message)

        if experiment:
            pass
            frame_metadata_event = create_event(event_type='frame', exp_id=experiment.exp_id, MoF=frame_metadata)
            # frame_metadata_event = create_event(event_type='frame', exp_id=1, MoF=frame_metadata)
            send_frame_to_storage_webpage(frame_metadata_event=frame_metadata_event,
                                          image_numpy=image_numpy,
                                          send_to_webpage=send_to_webpage)
        else:
            make_png(image_numpy)

    except ModExpError as e:
        if experiment is not None:
            experiment.stop_exception = e
            experiment.to_be_stopped = True
        return False, e

    return True, None


def send_frame_to_storage_webpage(frame_metadata_event, image_numpy, send_to_webpage):

    s = BytesIO()
    np.savez_compressed(s, frame_data=image_numpy)
    s.seek(0)
    data = {'data': json.dumps(frame_metadata_event)}
    files = {'file': s}
    send_to_storage(storage_uri=STORAGE_FRAMES_URI, data=data, files=files)


def send_to_storage(storage_uri, data, files=None):
    try:
        storage_resp = requests.post(storage_uri, files=files, data=data)
    except Exception as e:
        raise ModExpError(error='Problems with storage', exception_message='Could not send to storage' """e.message""")

    try:
        storage_resp_dict = json.loads(storage_resp.content)
    except (ValueError, TypeError):
        raise ModExpError(error='Problems with storage', exception_message='Storage\'s response is not JSON')

    if not ('result' in storage_resp_dict.keys()):
        raise ModExpError(error='Problems with storage',
                          exception_message="Storage\'s response has incorrect format (no 'result' key)")

    if storage_resp_dict['result'] != 'success':
        raise ModExpError(error='Problems with storage',
                          exception_message='Storage\'s response:  ' + str(storage_resp_dict['result']))


def make_png(image_numpy, png_filename=FRAME_PNG_FILENAME):
    res = image_numpy
    try:

        small_res = zoom(np.rot90(res), zoom=0.25, order=0)
        fig = plt.figure()
        img = plt.imshow(small_res)
        fig.colorbar(img)
        fig.tight_layout()
        plt.gray()
        plt.axis('off')
        plt.savefig(png_filename)

    except Exception as e:
        raise ModExpError(error="Could not make png-file from image", exception_message=e.message)


def send_message_to_storage_webpage(event_dict):
    event_json_for_storage = json.dumps(event_dict)
    try:
        send_to_storage(STORAGE_EXP_FINISH_URI, data=event_json_for_storage)
    except ModExpError as e:
        raise ModExpError(error="Could not message to storage", exception_message=e.message)


# Experiment
def check_and_prepare_exp_parameters(exp_param):
    if not (('exp_id' in exp_param.keys()) and ('advanced' in exp_param.keys())):
        return False, 'Incorrect format of keywords'
    if not ((type(exp_param['exp_id']) is str) and (type(exp_param['advanced']) is bool)):
        return False, 'Incorrect format: incorrect types'
    if exp_param['advanced']:

        if not ('instruction' in exp_param.keys()):
            return False, 'Incorrect format'
        if not (type(exp_param['instruction']) is str):
            return False, 'Type of instruction must be unicode'
        if exp_param['instruction'].find(".__") != -1:
            return False, 'Unacceptable instruction, there must not be substring ".__"'
        if exp_param['instruction'].find("t_0M_o_9_r_") != -1:
            return False, 'Unacceptable instruction, there must not be substring "t_0M_o_9_r_"'
    else:
        if not (('DARK' in exp_param.keys()) and ('EMPTY' in exp_param.keys()) and ('DATA' in exp_param.keys())):
            return False, 'Incorrect format3'
        if not ((type(exp_param['DARK']) is dict) and (type(exp_param['EMPTY']) is dict) and (
                    type(exp_param['DATA']) is dict)):
            return False, 'Incorrect format4'

        if not ('count' in exp_param['DARK'].keys()) and ('exposure' in exp_param['DARK'].keys()):
            return False, 'Incorrect format in \'DARK\' parameters'
        if not ((type(exp_param['DARK']['count']) is int) and (type(exp_param['DARK']['exposure']) is float)):
            return False, 'Incorrect format in \'DARK\' parameters'

        if not ('count' in exp_param['EMPTY'].keys()) and ('exposure' in exp_param['EMPTY'].keys()):
            return False, 'Incorrect format in \'EMPTY\' parameters'
        if not ((type(exp_param['EMPTY']['count']) is int) and (type(exp_param['EMPTY']['exposure']) is float)):
            return False, 'Incorrect format in \'EMPTY\' parameters'

        if not ('step count' in exp_param['DATA'].keys()) and ('exposure' in exp_param['DATA'].keys()):
            return False, 'Incorrect format in \'DATA\' parameters'
        if not ((type(exp_param['DATA']['step count']) is int) and (type(exp_param['DATA']['exposure']) is float)):
            return False, 'Incorrect format in \'DATA\' parameters'

        if not ('angle step' in exp_param['DATA'].keys()) and ('count per step' in exp_param['DATA'].keys()):
            return False, 'Incorrect format in \'DATA\' parameters'

        angle_step_correct_type = type(exp_param['DATA']['angle step']) is float
        count_per_step_correct_type = type(exp_param['DATA']['count per step']) is int
        delay_correct_type = type(exp_param['DATA']['delay']) is int

        if not (angle_step_correct_type and count_per_step_correct_type and delay_correct_type):
            return False, 'Incorrect format in \'DATA\' parameters'

        # TO DELETE AFTER WEB-PAGE OF ADJUSTMENT START CHECK PARAMETERS
        if exp_param['DARK']['exposure'] < 0.1:
            return False, 'Bad parameters in \'DARK\' parameters'
        if exp_param['EMPTY']['exposure'] < 0.1:
            return False, 'Bad parameters in \'EMPTY\' parameters'
        if exp_param['DATA']['exposure'] < 0.1:
            return False, 'Bad parameters in \'DATA\' parameters'

    # we don't multiply and round  exp_param['DATA']['angle step'] here, we will do it during experiment,
    # because it will be more accurate this way
    return True, ''
