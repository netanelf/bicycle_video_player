from main_controller import VlcPlayer
import logging
import config as cfg
import time
import os


class HistoryController(VlcPlayer):
    def __init__(self):
        super(HistoryController, self).__init__()
        self.thresh = cfg.THRESHOLD
        movie_path = os.path.join(os.path.basename(os.path.dirname(os.path.realpath(__file__))), cfg.MOVIE_FILENAME)
        self.load_movie(movie_path)
        self.speeds = {}
        self._logger = logging.getLogger(self.__class__.__name__)
        self.set_fullscreen()

    def run(self):
        self.play()
        time.sleep(0.1)
        self.pause()
        while True:
            time.sleep(0.1)
            toggle = False
            for key, value in self.speeds.iteritems():
                if value > self.thresh:
                    toggle = True
                    break
            if toggle and not self.is_playing():
                self.play()
                self._logger.debug('im toggling on!')
            elif not toggle and self.is_playing():
                self._logger.debug('im toggling off!')
                self.pause()

    def update_encoder(self, player_id, encoder_data):
        self._logger.debug('player id: {} data: {}'.format(player_id, encoder_data))
        self.speeds[player_id] = encoder_data * cfg.CONVERSION_FACTOR[player_id]
