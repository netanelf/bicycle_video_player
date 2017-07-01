from main_controller import VlcPlayer
import logging
import history_config as cfg
import time
import os


class HistoryController(VlcPlayer):

    def __init__(self):
        super(HistoryController, self).__init__()
        self.thresh = cfg.THRESHOLD
        self.movie_path = os.path.join(os.path.basename(os.path.dirname(os.path.realpath(__file__))), cfg.MOVIE_FILENAME)
        self.load_movie(self.movie_path)
        self.speeds = {}
        self._logger = logging.getLogger(self.__class__.__name__)
        self.set_fullscreen()
        self._movie_stopped_time = time.time()

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
                self._movie_stopped_time = time.time()
            if self.is_playing() is False \
                    and (time.time() - self._movie_stopped_time > cfg.HOLD_BEFORE_RESTART):
                self._logger.debug('bicycle idle for {} time, returning to default scene'.format(
                    time.time() - self._movie_stopped_time))
                self.set_position(0)
            self.restart_ended_video(self.movie_path, 0)

    def update_encoder(self, player_id, encoder_data):
        self._logger.debug('player id: {} data: {}'.format(player_id, encoder_data))
        self.speeds['{}'.format(player_id)] = encoder_data * cfg.CONVERSION_FACTOR

    def do_kaftor(self, kaftor_number):
        pass

if __name__ == '__main__':

    p = HistoryController()
    p.setDaemon(True)
    p.start()
    time.sleep(2)
    print("a")
    p.update_encoder(player_id=2, encoder_data=3000)
    time.sleep(2)
    print("a")
    p.update_encoder(player_id=1, encoder_data=1001)
    time.sleep(2)
    print("a")
    p.update_encoder(player_id=2, encoder_data=0)
    time.sleep(2)
    print("a")
    p.update_encoder(player_id=0, encoder_data=100)
    time.sleep(2)
    print("a")
    p.update_encoder(player_id=1, encoder_data=0)
    time.sleep(2)
    print("a")
    p.update_encoder(player_id=0, encoder_data=0)
    time.sleep(4)
    print("a")
    p.update_encoder(player_id=0, encoder_data=11)
    time.sleep(300)
