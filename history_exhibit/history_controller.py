import time

import logging

from main_controller import VlcPlayer
import config


class HistoryController(VlcPlayer):

    MOVIE = "movie.mp4"

    def __init__(self):
        super(HistoryController, self).__init__()
        self.thresh = config.THRESHOLD
        self.load_movie(self.MOVIE)
        self.speeds={}
        self._logger = logging.getLogger(self.__class__.__name__)


    def run(self):
        while True:
            time.sleep(0.1)
            toggle = False
            for key, value in self.speeds.iteritems():
                if value > self.thresh:
                    toggle = True
                    break
            if toggle and not self._is_playing:
                self.play()
                self._logger.debug('im toggling on!')
            elif not toggle and self._is_playing:
                self._logger.debug('im toggling off!')
                self.pause()

    def update_encoder(self, player_id, encoder_data):
        self._logger.debug('player id {}'.format(player_id))
        self.speeds[player_id] = encoder_data * config.CONVERSION_FACTOR[player_id]