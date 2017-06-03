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
        
        self.alive = True
        self._logger.info('finished initializing TourController')

    def run(self):
        while self.alive:
            time.sleep(0.5)
            #self.read_serial_data()
            # if we are not playing, change played movie
            ## button press

            # if frame number changes the load/fan state --> send data to arduino
            # set speed according to data

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
        #TODO
        pass

        
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
    init_logging('tour_controller', logging.INFO)
    p = TourController()
    p.setDaemon(True)
    p.start()
    time.sleep(3)
    
