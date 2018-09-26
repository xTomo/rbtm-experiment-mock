import json


EMERGENCY_STOP_MSG = 'Experiment was emergency stopped'


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
