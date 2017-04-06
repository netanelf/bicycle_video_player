from time import sleep
import threading
import logging
from bicycle_race_viewer import BicycleRaceViewer
import serial


class BicycleRaceController(threading.Thread):
    READ_TIMEOUT = 2
    PORT = 'COM40'
    BAUDRATE = 9600

    def __init__(self):
        self._logger = logging.getLogger(self.__class__.__name__)
        super(BicycleRaceController, self).__init__()
        self._viewer = BicycleRaceViewer()
        self._viewer.setDaemon(True)
        self._viewer.start()

        #TODO:  this should be fixed in BicycleRaceViewer, if no initial speed is given nothing is shown
        self._viewer.update_velocity(player=0, new_velocity=1)
        self._serial = serial.Serial(port=self.PORT,
                                     baudrate=self.BAUDRATE,
                                     bytesize=serial.EIGHTBITS,
                                     stopbits=serial.STOPBITS_ONE,
                                     parity=serial.PARITY_NONE,
                                     writeTimeout=2,
                                     timeout=self.READ_TIMEOUT)
        try:
            self._serial.open()
        except Exception as ex:
            self._logger.error(ex)
        self._logger.info('finished init')

    def run(self):
        while True:
            instruction = self.read_serial_data()
            self.update_values(instruction)

    def read_serial_data(self):
        reading = True
        raw_data = []
        while reading:
            try:
                d = self._serial.read(size=1)
                if d == '\n':
                    reading = False
                elif d != '':
                    raw_data.append(d)

            except Exception as ex:
                self._logger.error(ex)

        self._logger.debug(raw_data)

        op_id = int(raw_data[0])
        data = raw_data[1:]
        self._logger.debug('op_id: {}, data: {}'.format(op_id, data))

        return (op_id, data)

    def update_values(self, instruction):
        op_id, data = instruction
        if op_id in (0, 1):
            player = op_id
            encoder_delta = int(''.join(data))
            self._logger.debug('player: {}, encoder: {}'.format(player, encoder_delta))
            self._viewer.update_velocity(player=player, new_velocity=encoder_delta/100)


    def update_race_viewer(self, new_configuration):
        pass

if __name__ == '__main__':
    from bicycle_player import init_logging
    init_logging(logger_name='BicycleRaceController', logger_level=logging.INFO)

    controller = BicycleRaceController()
    controller.setDaemon(True)
    controller.start()

    while controller.is_alive():
        sleep(1)


