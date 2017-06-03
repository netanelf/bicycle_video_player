import logging
try:
    from main_controller import VlcPlayer
except ImportError:
    import sys
    sys.path.append('..')
    from main_controller import VlcPlayer
import tour_config as cfg
import time


class TourController(VlcPlayer):
    OPIDS  = {'DOWN_HILL': 0,
              'UP_HILL': 1,
              'MISHOR': 2
              }

    def __init__(self):
        super(TourController, self).__init__()
        self._logger = logging.getLogger(self.__class__.__name__)
        # initialize list of topographies
        # load movie associated with each route
        # initialize player
        
        self._alive = True
        self._speed = 0
        self._is_playing = False
        #TODO: I think __init__ should get the player_number as well and decide which movie to play (front/ back)
        self.load_movie(file=cfg.SCENES['default']['front_movie'])
        self._logger.info('finished initializing TourController')
    
    def run(self):
        while self._alive:
            if self._speed > cfg.SPEED_THRESHOLD and self._is_playing == False:
                self._start_graduel_playing()
            
            if self._speed <= cfg.SPEED_THRESHOLD and self._is_playing == True:
                self._start_graduel_stopping()     
            #self.read_serial_data()
            # if we are not playing, change played movie
            ## button press

            # if frame number changes the load/fan state --> send data to arduino
            # set speed according to data
    
    def _start_graduel_playing(self):
        self._logger.info('in _start_graduel_playing ')
        self._is_playing = True
        self.play()
        for (delta_t, speed) in cfg.SPEED_UP_RAMPING:
            self._logger.debug('setting speed = {}'.format(speed))
            self.update_speed(new_speed=speed)
            time.sleep(delta_t)
        self.update_speed(new_speed=1)
        
    def _start_graduel_stopping(self):
        self._logger.info('in _start_graduel_stopping ')
        self._is_playing = False
        self.pause()
        
    def send_serial_data(self, opid):
        # 3 states of DOWN_HILL/ UP_HILL / MISHOR
        pass

    def do_kaftor(self,kaftor_number):
        #TODO
        pass

    def has_send(self):
        #TODO
        pass

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
    p = TourController()
    p.setDaemon(True)
    p.start()
    time.sleep(2)
    p.update_encoder(player_id=0, encoder_data=3000)
    time.sleep(4)
    p.update_encoder(player_id=0, encoder_data=1001)
    time.sleep(4)
    p.update_encoder(player_id=0, encoder_data=500)
    time.sleep(4)