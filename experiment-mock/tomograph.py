from .modExpError import ModExpError


class Tomograph:

    def __init__(self):
        self.current_experiment = None
        self.source_current = None  # mock only property
        self.source_voltage = None  # mock only property

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

    def source_set_voltage(self, new_voltage, from_experiment=False):
        self.basic_tomo_check(from_experiment=from_experiment)

        if type(new_voltage) is not float:
            raise ModExpError(error='Incorrect format: type must be float')

        if new_voltage < 2 or 60 < new_voltage:
            raise ModExpError(error='Voltage must have value from 2 to 60!')

        self.source_voltage = new_voltage

    def source_set_current(self, new_current, from_experiment=False):
        self.basic_tomo_check(from_experiment=from_experiment)

        if type(new_current) is not float:
            raise ModExpError(error='Incorrect format: type must be float')

        if new_current < 2 or 80 < new_current:
            raise ModExpError(error='Current must have value from 2 to 80!')

        self.source_current = new_current

    def source_get_voltage(self, from_experiment=False):
        self.basic_tomo_check(from_experiment=from_experiment)
        return self.source_voltage

    def source_get_current(self, from_experiment=False):
        self.basic_tomo_check(from_experiment=from_experiment)
        return self.source_current
