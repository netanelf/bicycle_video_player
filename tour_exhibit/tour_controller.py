import logging
from bisect import bisect_left

# this is just for debug running through the __main__ function
try:
    from main_controller import VlcPlayer
except ImportError:
    import sys
    sys.path.append('..')
    from main_controller import VlcPlayer
import tour_config as cfg
import time


class TourController(VlcPlayer):
    topographies = {'DOWN_HILL': 0,
                    'UP_HILL': 1,
                    'MISHOR': 2
                     }

    def __init__(self, player_number):
        super(TourController, self).__init__()
        self._logger = logging.getLogger(self.__class__.__name__)

        self._speed = 0

        if player_number == 0:
            self.load_movie(file=cfg.SCENES['default']['front_movie'])
        elif player_number == 1:
            self.load_movie(file=cfg.SCENES['default']['back_movie'])
        else:
            self._logger.error('Wrong player number ({})'.format(player_number))

        self._logger.info('finished initializing TourController')
    
    def run(self):
        self._start_paused_movie()
        topography_struct = cfg.SCENES['default']['topography']
        topography_keys = topography_struct.keys()
        current_topography_index = -1
        while self._alive:
            if self._speed > cfg.SPEED_THRESHOLD and self._is_playing is False:
                self._start_gradual_playing()
            
            if self._speed <= cfg.SPEED_THRESHOLD and self._is_playing is True:
                self._start_gradual_stopping()

            t = self.get_time()
            self._logger.debug('time: {}'.format(t))

            try:
                if current_topography_index < len(topography_keys):
                    if t >= topography_keys[current_topography_index + 1]:  # we just passed to next topography
                        current_topography_index += 1
                        self._set_topography(topography_struct[topography_keys[current_topography_index]])
            except Exception as ex:
                self._logger.error('when trying to set topography got exception: {}'.format(ex))


            #self.read_serial_data()
            # if we are not playing, change played movie
            ## button press

            time.sleep(0.05)

    def _start_paused_movie(self):
        self.play()
        time.sleep(0.5)
        self.pause()

    def _set_topography(self, topography):
        """
        fan_0
        fan_1
        load_0
        load_1
        :param topography:
        :return:
        """
        self._logger.info('in _set_topography, topography: {}'.format(topography))
        if topography == self.topographies['DOWN_HILL']:
            self.data_to_send.put('load_0')
            self.data_to_send.put('fan_1')
        elif topography == self.topographies['UP_HILL']:
            self.data_to_send.put('fan_0')
            self.data_to_send.put('load_1')
        elif topography == self.topographies['MISHOR']:
            self.data_to_send.put('load_0')
            self.data_to_send.put('fan_0')
        else:
            self._logger.error('unknown topography ({})'.format(topography))

    def _start_gradual_playing(self):
        self._logger.info('in _start_gradual_playing ')
        self.play()
        self.gradual_speed_change(steps=cfg.SPEED_UP_RAMPING)
        self.update_speed(new_speed=1)
        
    def _start_gradual_stopping(self):
        self._logger.info('in _start_gradual_stopping ')
        self.gradual_speed_change(steps=cfg.SPEED_DOWN_RAMPING)
        self.pause()

    def do_kaftor(self, kaftor_number):
        self._logger.info('button {} was pushed'.format(kaftor_number))

    def update_encoder(self, player_id, encoder_data):
        self._logger.debug('in update_encoder, player_id= {}, encoder_data= {}'.format(player_id, encoder_data))
        self._speed = encoder_data / float(cfg.ENCODER_TO_SPEED_CONVERSION)
        
        
def init_logging(log_name, logger_level):
    logger = logging.getLogger()
    s_handler = logging.StreamHandler()
    f_handler = RotatingFileHandler(filename=os.path.join('..', 'logs', '{}_{}.log'
                                            .format(log_name, datetime.now()
                                                    .strftime('%d-%m-%y_%H-%M-%S'))),
                                    maxBytes=10E6,
                                    backupCount=500)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    s_handler.setFormatter(formatter)
    f_handler.setFormatter(formatter)
    logger.addHandler(s_handler)
    logger.addHandler(f_handler)
    logger.setLevel(logger_level)
    
if __name__ == '__main__':
    from logging.handlers import RotatingFileHandler
    import os
    from datetime import datetime
    init_logging('tour_controller', logging.DEBUG)
    p = TourController(player_number=0)
    p.setDaemon(True)
    p.start()
    time.sleep(30)
    p.update_encoder(player_id=0, encoder_data=3000)
    time.sleep(5)
    p.update_encoder(player_id=0, encoder_data=1001)
    time.sleep(5)
    p.update_encoder(player_id=0, encoder_data=500)
    time.sleep(10)
