import time
import threading
import logging
from bicycle_race_viewer import BicycleRaceViewer
import bicycle_race_config as cfg


class RaceController(threading.Thread):
    # READ_TIMEOUT = 2
    # PORT = '/dev/ttyUSB0' #'COM40'
    # BAUDRATE = 9600

    def __init__(self, dir_name=cfg.GRAPHICS_DICTIONARY):
        self._logger = logging.getLogger(self.__class__.__name__)
        super(RaceController, self).__init__()
        self._viewer = BicycleRaceViewer(dir_name)
        self._viewer.setDaemon(True)
        self._viewer.start()
        self._logger.info('finished init')

    def run(self):
        while True:
            time.sleep(1)

    def update_encoder(self, player_id, encoder_delta):
        new_velocity = encoder_delta / cfg.SPEED_FACTOR[player_id]
        if player_id in (0,2):
            player_id = 0
        elif player_id in (1,3):
            player_id = 1
        self.update_speed(player_id, new_velocity)
    
    def update_speed(self, player_id, speed):
        self._viewer._update_velocity(player=player_id, new_velocity=speed)

    def update_race_viewer(self, new_configuration):
        pass

if __name__ == '__main__':
    from bicycle_player import init_logging
    # init_logging(logger_name='BicycleRaceController', logger_level=logging.INFO)

    controller = RaceController("bicycle_race_sample_pics")
    controller.setDaemon(True)
    controller.start()

    while controller.is_alive():
        time.sleep(1)


