from .modExpError import ModExpError


class Tomograph:

    def __init__(self):
        self.current_experiment = None

    def basic_tomo_check(self, from_experiment):
        if not from_experiment:
            if self.current_experiment is not None:
                raise ModExpError(error='On this tomograph experiment is running')
        else:
            if self.current_experiment.to_be_stopped:
                raise self.current_experiment.stop_exception

    def tomo_state(self):
        if self.current_experiment is not None:
            return 'experiment', ""
        else:
            return 'ready', ""

    def source_power_on(self, from_experiment=False):
        self.basic_tomo_check(from_experiment)

    def source_power_off(self, from_experiment=False):
        self.basic_tomo_check(from_experiment)
